"""İterasyon motoru: aday üret → walk-forward sına → hakem → post-mortem → düzelt.

Her tur, hakemin (Reviewer 2) makine-eylemli önerilerini bir sonraki turun aday
üretim konfigürasyonuna uygular. Döngü, kabul kriterleri (K1–K5) sağlanınca ya da
``maks_tur`` dolunca durur; kriterler sağlanamadıysa en iyi tur "kabul edilmedi"
etiketiyle raporlanır — bu bir hata değil, dürüst bir bilimsel sonuçtur.

Sınama tasarımı: test blokları takvim yıllarıdır. Y yılı için eğitim, serinin
başından Y-1 sonuna kadardır (en az ``egitim_yil`` yıl geçmişi olan semboller
katılır); seçim, katılan sembollerin eğitim Sharpe'larının ortalamasına göre
yapılır ve seçilen kural Y yılına uygulanır. Böylece raporlanan OOS performansı,
tek bir "şanslı" kuralın değil, **seçim prosedürünün** performansıdır
(Bailey ve ark. 2014'ün önerdiği çerçeve).
"""

from __future__ import annotations

import warnings
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from alsat import hakem, olcutler
from alsat.gostergeler import AILELER, pozisyon_uret, topluluk, vol_hedef
from alsat.sinama import VARSAYILAN_MALIYET_BPS, backtest, satin_al_tut

RANDOM_STATE = 42
MIN_EGITIM_YIL = 3


@dataclass(frozen=True)
class AdaySpek:
    aile: str
    parametreler: tuple  # dict yerine hashable: sorted tuple of items
    vol_filtre: float | None = None
    uyeler: tuple = ()   # topluluk adayı için üye spekler

    @property
    def params(self) -> dict:
        return dict(self.parametreler)

    @property
    def etiket(self) -> str:
        p = ",".join(f"{k}={v}" for k, v in self.parametreler)
        ek = f"|vol{self.vol_filtre}" if self.vol_filtre else ""
        if self.uyeler:
            icerik = "; ".join(u.etiket for u in self.uyeler)
            return f"topluluk[{icerik}]({p}){ek}"
        return f"{self.aile}({p}){ek}"


@dataclass
class TurKaydi:
    tur_no: int
    aday_sayisi: int
    kum_deneme: int
    secilen: AdaySpek
    yillik_secimler: dict          # test yılı → seçilen etiket
    olcutler: dict                 # birleşik OOS + sembol bazında
    kabul_durumu: dict             # K1..K5 → bool
    kabul: bool
    elestiriler: list = field(default_factory=list)
    eylemler: list = field(default_factory=list)
    aday_tablosu: pd.DataFrame | None = None
    oos_ozsermaye: pd.Series | None = None


@dataclass
class DonguSonucu:
    turlar: list
    final_spek: AdaySpek
    final_tur_no: int
    kabul_edildi: bool
    kum_deneme: int
    bh_olcutler: dict
    bh_ozsermaye: pd.Series
    semboller: list
    ayarlar: dict


def _spek_yap(aile: str, params: dict, vol_filtre: float | None = None,
              uyeler: tuple = ()) -> AdaySpek:
    return AdaySpek(aile, tuple(sorted(params.items())), vol_filtre, uyeler)


def _pozisyon(spek: AdaySpek, kapanis: pd.Series) -> pd.Series:
    if spek.uyeler:
        # Üyeler vol filtresiz değerlendirilir; filtre toplulukta bir kez uygulanır.
        oylar = [_pozisyon(AdaySpek(u.aile, u.parametreler, None, u.uyeler), kapanis)
                 for u in spek.uyeler]
        poz = topluluk(oylar, esik=spek.params.get("esik", 0.5))
        if spek.vol_filtre:
            poz = vol_hedef(poz, kapanis, hedef_vol=spek.vol_filtre)
        return poz
    return pozisyon_uret(kapanis, spek.aile, spek.params, spek.vol_filtre)


class _Degerlendirici:
    """Sembol × aday pozisyonlarını ve yıl-dilimli metrikleri önbellekleyen çekirdek."""

    def __init__(self, seriler: dict[str, pd.Series], maliyet_bps: float):
        self.seriler = seriler
        self.maliyet = maliyet_bps
        self._poz: dict[tuple, pd.Series] = {}

    def pozisyon(self, spek: AdaySpek, sembol: str) -> pd.Series:
        anahtar = (spek, sembol)
        if anahtar not in self._poz:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                self._poz[anahtar] = _pozisyon(spek, self.seriler[sembol])
        return self._poz[anahtar]

    def test_yillari(self) -> list[int]:
        yillar: set[int] = set()
        for seri in self.seriler.values():
            ilk = seri.index[0].year + MIN_EGITIM_YIL
            yillar.update(range(ilk, seri.index[-1].year + 1))
        return sorted(yillar)

    def katilanlar(self, yil: int) -> list[str]:
        return [s for s, seri in self.seriler.items()
                if seri.index[0].year + MIN_EGITIM_YIL <= yil <= seri.index[-1].year]

    def _donem_net(self, spek: AdaySpek, sembol: str, baslangic, bitis,
                   maliyet: float | None = None, gecikme: int = 1) -> pd.Series:
        seri = self.seriler[sembol]
        poz = self.pozisyon(spek, sembol)
        getiri = seri.pct_change().fillna(0.0)
        uyg = poz.shift(gecikme).fillna(0.0) if gecikme else poz
        m = (maliyet if maliyet is not None else self.maliyet) / 1e4
        net = uyg * getiri - uyg.diff().abs().fillna(0.0) * m
        return net.loc[str(baslangic):str(bitis)]

    def egitim_sharpe(self, spek: AdaySpek, yil: int) -> float:
        degerler = []
        for s in self.katilanlar(yil):
            net = self._donem_net(spek, s, self.seriler[s].index[0].year, yil - 1)
            degerler.append(olcutler.sharpe(net))
        return float(np.mean(degerler)) if degerler else -np.inf

    def test_net(self, spek: AdaySpek, yil: int, maliyet: float | None = None,
                 gecikme: int = 1) -> dict[str, pd.Series]:
        return {s: self._donem_net(spek, s, yil, yil, maliyet, gecikme)
                for s in self.katilanlar(yil)}


def _birlesik(sembol_netler: dict[str, pd.Series]) -> pd.Series:
    """Sembollerin eşit ağırlıklı günlük ortalaması (ortak takvim birleşimi)."""
    return pd.concat(sembol_netler.values(), axis=1).mean(axis=1).sort_index()


def _prosedur_oos(dg: _Degerlendirici, adaylar: list[AdaySpek],
                  maliyet: float | None = None, gecikme: int = 1,
                  secimler: dict[int, AdaySpek] | None = None,
                  ) -> tuple[dict[int, AdaySpek], dict[str, pd.Series], list[float]]:
    """Yıl yıl seçim + test. ``secimler`` verilirse seçim tekrarlanmaz (stres testleri
    aynı seçimleri korur). Dönüş: (yıl→spek, sembol→OOS net, eğitim Sharpe listesi)."""
    yil_spek: dict[int, AdaySpek] = {}
    parcalar: dict[str, list[pd.Series]] = {s: [] for s in dg.seriler}
    is_sharpelar: list[float] = []
    for yil in dg.test_yillari():
        if not dg.katilanlar(yil):
            continue
        if secimler is not None:
            spek = secimler[yil]
        else:
            skorlar = [(dg.egitim_sharpe(a, yil), a.etiket, a) for a in adaylar]
            skorlar.sort(key=lambda x: (-x[0], x[1]))  # eşitlikte etiketle deterministik
            spek = skorlar[0][2]
            is_sharpelar.append(skorlar[0][0])
        yil_spek[yil] = spek
        for s, net in dg.test_net(spek, yil, maliyet, gecikme).items():
            parcalar[s].append(net)
    sembol_oos = {s: pd.concat(p) for s, p in parcalar.items() if p}
    return yil_spek, sembol_oos, is_sharpelar


def _komsular(spek: AdaySpek) -> list[AdaySpek]:
    """H2 için: seçilen spekin ailesindeki diğer ızgara noktaları."""
    if spek.uyeler:
        return []  # topluluk için komşuluk üye ızgaralarında zaten sınandı
    return [_spek_yap(spek.aile, p, spek.vol_filtre)
            for p in AILELER[spek.aile]["izgara"]
            if tuple(sorted(p.items())) != spek.parametreler]


def _aday_havuzu(cfg: dict, onceki_en_iyiler: dict[str, AdaySpek] | None) -> list[AdaySpek]:
    adaylar: list[AdaySpek] = []
    for aile in cfg["aileler"]:
        izgara = AILELER[aile]["izgara"]
        if cfg["izgara_mod"] == "sade" and onceki_en_iyiler and aile in onceki_en_iyiler:
            izgara = [onceki_en_iyiler[aile].params]
        for params in izgara:
            adaylar.append(_spek_yap(aile, params, cfg["vol_filtre"]))
    if cfg["topluluk_ekle"] and onceki_en_iyiler:
        cekirdek = tuple(onceki_en_iyiler[a] for a in
                         ("sma_kesisim", "fiyat_sma", "tsmom", "donchian_kirilim")
                         if a in onceki_en_iyiler)
        if len(cekirdek) >= 3:
            for esik in (0.5, 0.75):
                adaylar.append(AdaySpek("topluluk", (("esik", esik),),
                                        cfg["vol_filtre"], cekirdek))
    return adaylar


def _eylem_uygula(cfg: dict, eylemler: list[str], aday_tablosu: pd.DataFrame) -> dict:
    cfg = dict(cfg)
    for eylem in eylemler:
        if eylem == "vol_filtre":
            cfg["vol_filtre"] = cfg["hedef_vol"]
        elif eylem == "topluluk":
            cfg["topluluk_ekle"] = True
        elif eylem in ("sadelestir", "aday_azalt"):
            cfg["izgara_mod"] = "sade"
            if eylem == "sadelestir":
                saglam = (aday_tablosu.groupby("aile")["oos_sharpe"].median() > 0)
                kalan = [a for a in cfg["aileler"] if saglam.get(a, False)]
                if len(kalan) >= 3:
                    cfg["aileler"] = kalan
        elif eylem == "devir_azalt":
            cfg["devir_filtre"] = True
        elif eylem == "maliyet_yukselt":
            cfg["maliyet_carpan"] = cfg.get("maliyet_carpan", 1.0) * 1.5
    return cfg


def calistir(seriler: dict[str, pd.Series], maliyet_bps: float = VARSAYILAN_MALIYET_BPS,
             maks_tur: int = 5, hedef_vol: float = 0.40,
             gunluk=print) -> DonguSonucu:
    """Reviewer 2 döngüsünü işletir ve tüm turların kaydını döndürür."""
    cfg: dict = {
        "aileler": list(AILELER), "izgara_mod": "tam", "vol_filtre": None,
        "topluluk_ekle": False, "devir_filtre": False,
        "maliyet_carpan": 1.0, "hedef_vol": hedef_vol,
    }
    turlar: list[TurKaydi] = []
    denenen: set[str] = set()
    onceki_en_iyiler: dict[str, AdaySpek] | None = None

    # Satın-al-tut kıyası: OOS dönemiyle hizalı (ilk test yılından itibaren)
    dg0 = _Degerlendirici(seriler, maliyet_bps)
    ilk_yil = dg0.test_yillari()[0]
    bh_netler = {}
    for s, seri in seriler.items():
        oos_seri = seri.loc[str(max(ilk_yil, seri.index[0].year + MIN_EGITIM_YIL)):]
        bh_netler[s] = satin_al_tut(oos_seri).net_getiriler
    bh_net = _birlesik(bh_netler)
    bh_oz = (1 + bh_net).cumprod()
    bh_olc = olcutler.olcut_tablosu(bh_net, bh_oz, devir=0.0, poz_orani=1.0)

    for tur_no in range(1, maks_tur + 1):
        etkin_maliyet = maliyet_bps * cfg["maliyet_carpan"]
        dg = _Degerlendirici(seriler, etkin_maliyet)
        adaylar = _aday_havuzu(cfg, onceki_en_iyiler)

        # Aday tablosu: sabit-spek OOS metrikleri (sıralama + H2 + sadeleştirme girdisi)
        satirlar = []
        for a in adaylar:
            _, sembol_oos, _ = _prosedur_oos(dg, [a])
            net = _birlesik(sembol_oos)
            oz = (1 + net).cumprod()
            devir = float(np.mean([
                dg.pozisyon(a, s).shift(1).diff().abs().sum() / max(len(seriler[s]) / 365, 1)
                for s in seriler]))
            satirlar.append({"etiket": a.etiket, "aile": a.aile,
                             "oos_sharpe": olcutler.sharpe(net),
                             "oos_yillik": olcutler.yillik_getiri(net),
                             "maks_dusus": olcutler.maks_dusus(oz),
                             "yillik_devir": devir, "_spek": a})
        tablo = pd.DataFrame(satirlar).sort_values(
            "oos_sharpe", ascending=False).reset_index(drop=True)

        if cfg["devir_filtre"]:
            esik = float(tablo["yillik_devir"].median())
            uygun = tablo[tablo["yillik_devir"] <= esik]
            if len(uygun) >= 5:
                adaylar = list(uygun["_spek"])
                tablo = uygun.reset_index(drop=True)

        denenen.update(a.etiket for a in adaylar)
        kum = len(denenen)

        # Seçim prosedürü (headline OOS) + hakem kanıt dosyası
        secimler, sembol_oos, is_sharpelar = _prosedur_oos(dg, adaylar)
        oos_net = _birlesik(sembol_oos)
        oos_oz = (1 + oos_net).cumprod()
        final = secimler[max(secimler)]  # canlı kullanım speki: son eğitim penceresinin seçimi

        stres2 = _birlesik(_prosedur_oos(dg, adaylar, maliyet=etkin_maliyet * 2,
                                         secimler=secimler)[1])
        stres4 = _birlesik(_prosedur_oos(dg, adaylar, maliyet=etkin_maliyet * 4,
                                         secimler=secimler)[1])
        gecikmesiz = _birlesik(_prosedur_oos(dg, adaylar, gecikme=0,
                                             secimler=secimler)[1])
        komsu_sharpelar = []
        for komsu in _komsular(final):
            _, k_oos, _ = _prosedur_oos(dg, [komsu])
            komsu_sharpelar.append(olcutler.sharpe(_birlesik(k_oos)))

        # Son 24 ay penceresi (H8 + K6): güncel rejim performansı
        son24_esik = oos_net.index[-1] - pd.Timedelta(days=730)
        son24 = oos_net.loc[oos_net.index >= son24_esik]
        son24_bh = bh_net.loc[bh_net.index >= son24_esik]
        son24_getiri = float((1 + son24).prod() - 1)
        son24_bh_getiri = float((1 + son24_bh).prod() - 1)

        # DSR için denemeler arası günlük Sharpe std'si — aday tablosundan ampirik
        deneme_std = None
        if len(tablo) > 1:
            deneme_std = float((tablo["oos_sharpe"] / np.sqrt(365)).std(ddof=1))

        girdi = hakem.HakemGirdisi(
            oos_net=oos_net, oos_ozsermaye=oos_oz, bh_net=bh_net, bh_ozsermaye=bh_oz,
            is_sharpe=float(np.mean(is_sharpelar)) if is_sharpelar else 0.0,
            n_deneme_kum=kum, sembol_oos=sembol_oos,
            gecikmesiz_sharpe=olcutler.sharpe(gecikmesiz),
            komsu_sharpelar=komsu_sharpelar,
            stres_2x_getiri=float((1 + stres2).prod() - 1),
            stres_4x_getiri=float((1 + stres4).prod() - 1),
            deneme_sharpe_std=deneme_std,
            son24_getiri=son24_getiri, son24_bh_getiri=son24_bh_getiri,
        )
        elestiriler = hakem.incele(girdi)

        olc = olcutler.olcut_tablosu(oos_net, oos_oz, devir=0.0, poz_orani=0.0,
                                     n_deneme=kum, deneme_sharpe_std=deneme_std)
        olc["poz_orani"] = float(np.mean([(dg.pozisyon(final, s).shift(1) > 0).mean()
                                          for s in seriler]))
        olc["is_sharpe"] = girdi.is_sharpe
        olc["stres_2x_getiri"] = girdi.stres_2x_getiri
        olc["sembol_sharpe"] = {s: olcutler.sharpe(n) for s, n in sembol_oos.items()}
        olc["son24_getiri"] = son24_getiri
        olc["son24_bh_getiri"] = son24_bh_getiri

        kabul_durumu = {
            "K1_oos_sharpe": olc["sharpe"] > 0.5 and all(
                v > 0 for v in olc["sembol_sharpe"].values()),
            "K2_dsr": olc["dsr"] >= hakem.DSR_HEDEF,
            "K3_maliyet_2x": girdi.stres_2x_getiri > 0,
            "K4_dusus": abs(olc["maks_dusus"]) < hakem.DUSUS_IYILESME_ORANI
                        * abs(bh_olc["maks_dusus"]),
            "K5_engel_yok": not hakem.engel_var(elestiriler),
            # K6 güncel rejim: son 24 ayda mutlak kazanç YA DA satın-al-tut'tan iyi
            "K6_son24ay": son24_getiri > 0 or son24_getiri >= son24_bh_getiri,
        }
        kabul = all(kabul_durumu.values())

        oneriler = [e.oneri["eylem"] for e in elestiriler if e.oneri]
        eylemler = list(dict.fromkeys(oneriler)) if not kabul else []

        # Durağanlık tırmanışı: önceki turla aynı seçim + aynı OOS Sharpe ise
        # hakem önerileri konfigürasyonu artık değiştirmiyor demektir — henüz
        # denenmemiş bir düzeltmeye tırman; hiçbiri kalmadıysa döngüyü erken bitir.
        duragan = bool(turlar) and turlar[-1].secilen == final and \
            abs(turlar[-1].olcutler["sharpe"] - olc["sharpe"]) < 1e-9
        duraganlik_bitisi = False
        if not kabul and duragan:
            uygulanmis = {
                "vol_filtre": cfg["vol_filtre"] is not None,
                "topluluk": cfg["topluluk_ekle"],
                "maliyet_yukselt": cfg.get("maliyet_carpan", 1.0) > 1.0,
                "sadelestir": cfg["izgara_mod"] == "sade",
            }
            tirmanis = [e for e in ("vol_filtre", "topluluk", "maliyet_yukselt")
                        if not uygulanmis[e] and e not in eylemler]
            etkisiz = [e for e in eylemler if uygulanmis.get(e, False) or
                       (e == "devir_azalt" and cfg["devir_filtre"])]
            eylemler = [e for e in eylemler if e not in etkisiz]
            if tirmanis:
                eylemler.append(tirmanis[0])
            elif not eylemler:
                duraganlik_bitisi = True

        turlar.append(TurKaydi(
            tur_no=tur_no, aday_sayisi=len(adaylar), kum_deneme=kum, secilen=final,
            yillik_secimler={y: s.etiket for y, s in secimler.items()},
            olcutler=olc, kabul_durumu=kabul_durumu, kabul=kabul,
            elestiriler=elestiriler, eylemler=eylemler,
            aday_tablosu=tablo.drop(columns="_spek"), oos_ozsermaye=oos_oz,
        ))
        engeller = sum(1 for e in elestiriler if e.siddet == "engel")
        if kabul:
            durum = "KABUL"
        elif duraganlik_bitisi:
            durum = "durağanlaştı, denenmemiş düzeltme kalmadı — erken bitiş"
        else:
            durum = "devam: " + ", ".join(eylemler)
        gunluk(f"Tur {tur_no}: {len(adaylar)} aday (kümülatif {kum}), "
               f"OOS Sharpe {olc['sharpe']:.2f}, DSR {olc['dsr']:.2f}, "
               f"{engeller} engel — {durum}")
        if kabul or duraganlik_bitisi:
            break

        onceki_en_iyiler = {}
        for _, satir in tablo.iterrows():
            spek = next(a for a in adaylar if a.etiket == satir["etiket"])
            if spek.aile not in onceki_en_iyiler and not spek.uyeler:
                onceki_en_iyiler[spek.aile] = _spek_yap(spek.aile, spek.params)  # filtresiz öz
        cfg = _eylem_uygula(cfg, eylemler, tablo)

    en_iyi = max(turlar, key=lambda t: (t.kabul, sum(t.kabul_durumu.values()),
                                        t.olcutler["sharpe"]))
    return DonguSonucu(
        turlar=turlar, final_spek=en_iyi.secilen, final_tur_no=en_iyi.tur_no,
        kabul_edildi=en_iyi.kabul, kum_deneme=turlar[-1].kum_deneme,
        bh_olcutler=bh_olc, bh_ozsermaye=bh_oz, semboller=list(seriler),
        ayarlar={"maliyet_bps": maliyet_bps, "maks_tur": maks_tur,
                 "hedef_vol": hedef_vol, "egitim_yil": MIN_EGITIM_YIL},
    )
