"""Geri-test motoru (aylık veri, uzun/nakit; açığa satış yok).

Kurallar:
- Pozisyon t ayı kapanışındaki bilgiyle belirlenir ve t→t+1 getirisine uygulanır
  (bakış-ileri sızıntısı yok). Kâhin stratejileri bunu bilerek ihlal eder ve
  yalnızca "üst sınır" olarak raporlanır.
- İşlem maliyeti, pozisyon her değiştiğinde portföy değerinin sabit bir oranı
  olarak düşülür (tek yön).
- Nakitteyken getiri `nakit_getiri` serisiyle verilir; yoksa 0 kabul edilir.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path

import numpy as np
import pandas as pd

VERI_YOLU = Path(__file__).resolve().parent / "veri" / "sp500_aylik_shiller.csv"
AYDA = 12


# --------------------------------------------------------------------------- veri
def veri_yukle(yol: Path | str | None = None) -> pd.DataFrame:
    """Shiller aylık S&P 500 tablosunu yükler; sıfır/eksik alanları NaN yapar.

    Sütunlar: fiyat, temettu (yıllık, aylık ortalamaya bölünmemiş), uzun_faiz (10y, %).
    Kaynak: https://github.com/datasets/s-and-p-500 (Robert Shiller verisi).
    Not: tarihsel satırlar ayın *ortalama* kapanışıdır, ay-sonu değil.
    """
    df = pd.read_csv(yol or VERI_YOLU, parse_dates=["Date"])
    df = df.rename(
        columns={
            "Date": "tarih",
            "SP500": "fiyat",
            "Dividend": "temettu",
            "Long Interest Rate": "uzun_faiz",
        }
    )[["tarih", "fiyat", "temettu", "uzun_faiz"]]
    df = df.set_index("tarih").sort_index()
    for kolon in ("temettu", "uzun_faiz"):
        df.loc[df[kolon] <= 0, kolon] = np.nan
    df = df[df["fiyat"] > 0]
    return df


def nakit_getirisi(df: pd.DataFrame) -> pd.Series:
    """Nakit için kaba bir vekil: 10 yıllık tahvil faizi / 12 (aylık).

    Bu bir T-bill değil; bazı dönemlerde nakit getirisini abartır. Sonuçlarda
    'nakit faizli' varyant bu yüzden yalnızca duyarlılık analizi olarak okunmalı.
    Faizin bulunmadığı aylarda 0.
    """
    return (df["uzun_faiz"].fillna(0.0) / 100.0 / AYDA).rename("nakit")


def toplam_getiri_fiyati(df: pd.DataFrame) -> pd.Series:
    """Temettüleri yeniden yatırarak toplam-getiri endeksi kurar (temettü verisi olan aylar).

    Yıllık temettü / 12 her ay fiyata bölünüp getiriye eklenir. Temettü verisinin
    bittiği aydan sonra yalnızca fiyat getirisi kullanılır (ve bu belirtilir).
    """
    fiyat = df["fiyat"]
    tem = (df["temettu"].fillna(0.0) / AYDA)
    getiri = fiyat.pct_change().fillna(0.0) + (tem / fiyat.shift(1)).fillna(0.0)
    return (1 + getiri).cumprod().rename("toplam_getiri")


# ---------------------------------------------------------------------- sinyaller
def al_ve_tut(fiyat: pd.Series) -> pd.Series:
    return pd.Series(1, index=fiyat.index, name="al_ve_tut")


def sma_kurali(fiyat: pd.Series, n: int = 10) -> pd.Series:
    """Fiyat > n-aylık basit hareketli ortalama ise piyasada (Faber 2007 kuralı)."""
    if n < 1:
        raise ValueError("n >= 1 olmalı")
    sma = fiyat.rolling(n).mean()
    poz = (fiyat > sma).astype(int)
    poz[sma.isna()] = 0
    return poz.rename(f"sma{n}")


def kesisim_kurali(fiyat: pd.Series, kisa: int = 2, uzun: int = 10) -> pd.Series:
    """Kısa HO > uzun HO ise piyasada ('altın/ölüm kesişimi' aylık karşılığı)."""
    if not 1 <= kisa < uzun:
        raise ValueError("1 <= kisa < uzun olmalı")
    k = fiyat.rolling(kisa).mean()
    u = fiyat.rolling(uzun).mean()
    poz = (k > u).astype(int)
    poz[u.isna()] = 0
    return poz.rename(f"kesisim{kisa}_{uzun}")


def mukemmel_ongoru(fiyat: pd.Series) -> pd.Series:
    """KÂHİN: gelecek ayın getirisi pozitifse piyasada. Bakış-ileri sızıntısı kasıtlı."""
    ileri = fiyat.shift(-1) / fiyat - 1
    poz = (ileri > 0).astype(int)
    poz.iloc[-1] = 0
    return poz.rename("kahin_aylik")


def zigzag_donusler(fiyat: pd.Series, esik: float = 0.20) -> list[tuple[pd.Timestamp, str]]:
    """Fiyat serisinde >= esik büyüklüğündeki dip/tepe dönüşlerini işaretler.

    Dönüş listesi [(tarih, 'dip'|'tepe'), ...] sırayla döner. Son aday dönüş,
    esik teyidi alamadıysa listeye girmez.
    """
    if not 0 < esik < 1:
        raise ValueError("0 < esik < 1 olmalı")
    v = fiyat.to_numpy()
    idx = fiyat.index
    donusler: list[tuple[pd.Timestamp, str]] = []
    yon = 0  # 0: henüz yön yok, +1 yükseliş (son dönüş dip), -1 düşüş (son dönüş tepe)
    maks_i = 0  # son dönüşten bu yana en yüksek
    min_i = 0  # son dönüşten bu yana en düşük
    for i in range(1, len(v)):
        if yon == 0:
            if v[i] > v[maks_i]:
                maks_i = i
            if v[i] < v[min_i]:
                min_i = i
            if v[i] <= v[maks_i] * (1 - esik):
                donusler.append((idx[maks_i], "tepe"))
                yon, min_i = -1, i
            elif v[i] >= v[min_i] * (1 + esik):
                donusler.append((idx[min_i], "dip"))
                yon, maks_i = +1, i
        elif yon > 0:
            if v[i] > v[maks_i]:
                maks_i = i
            elif v[i] <= v[maks_i] * (1 - esik):
                donusler.append((idx[maks_i], "tepe"))
                yon, min_i = -1, i
        else:
            if v[i] < v[min_i]:
                min_i = i
            elif v[i] >= v[min_i] * (1 + esik):
                donusler.append((idx[min_i], "dip"))
                yon, maks_i = +1, i
    return donusler


def dip_tepe_kahini(fiyat: pd.Series, esik: float = 0.20) -> pd.Series:
    """KÂHİN: gerçek dipte al, gerçek tepede sat (zigzag). Soru tam olarak bunu istiyor.

    Gelecek bilgisi kullanır; gerçekleştirilemez. Yalnızca 'ödülün büyüklüğünü'
    ve gecikme maliyetini ölçmek için referans.
    """
    donusler = zigzag_donusler(fiyat, esik)
    poz = pd.Series(0, index=fiyat.index)
    icinde = False
    baslangic = None
    for tarih, tur in donusler:
        if tur == "dip" and not icinde:
            icinde, baslangic = True, tarih
        elif tur == "tepe" and icinde:
            poz.loc[baslangic:tarih] = 1
            poz.loc[tarih] = 0  # tepe ayında sat: t→t+1 getirisini alma
            icinde = False
    if icinde and baslangic is not None:
        # son dipten sonra teyitli tepe yok: kâhin yine de son dipten sonraki en yüksekte satar
        son_tepe = fiyat.loc[baslangic:].idxmax()
        poz.loc[baslangic:son_tepe] = 1
        poz.loc[son_tepe] = 0
    return poz.rename(f"kahin_zigzag{int(esik*100)}")


# ---------------------------------------------------------------------- geri test
@dataclass
class Sonuc:
    ad: str
    baslangic: str
    bitis: str
    yil: float
    cagr: float
    yillik_oynaklik: float
    sharpe_rf0: float
    max_dusus: float
    son_deger: float
    islem_sayisi: int
    piyasada_oran: float

    def satir(self) -> dict:
        return asdict(self)


def _max_dusus(seri: pd.Series) -> float:
    zirve = seri.cummax()
    return float((seri / zirve - 1).min())


def geri_test(
    fiyat: pd.Series,
    pozisyon: pd.Series,
    maliyet: float = 0.0,
    nakit_getiri: pd.Series | None = None,
    ad: str | None = None,
) -> tuple[pd.Series, Sonuc]:
    """Pozisyon serisini fiyata uygular; (özkaynak eğrisi, Sonuc) döner.

    pozisyon[t] ∈ {0,1}, t kapanışında belirlenir, t→t+1 getirisine uygulanır.
    """
    if maliyet < 0:
        raise ValueError("maliyet negatif olamaz")
    fiyat = fiyat.astype(float)
    poz = pozisyon.reindex(fiyat.index).fillna(0).astype(int)
    getiri = fiyat.pct_change().fillna(0.0)
    nakit = (
        nakit_getiri.reindex(fiyat.index).fillna(0.0)
        if nakit_getiri is not None
        else pd.Series(0.0, index=fiyat.index)
    )
    poz_onceki = poz.shift(1).fillna(0).astype(int)
    port_getiri = poz_onceki * getiri + (1 - poz_onceki) * nakit
    degisim = (poz != poz_onceki).astype(int)
    degisim.iloc[0] = 0
    # maliyet: pozisyonun değiştiği ayın kapanışında düşülür
    port_getiri = (1 + port_getiri) * (1 - maliyet * degisim) - 1
    ozkaynak = (1 + port_getiri).cumprod()
    yil = max((fiyat.index[-1] - fiyat.index[0]).days / 365.25, 1e-9)
    cagr = float(ozkaynak.iloc[-1] ** (1 / yil) - 1)
    oyn = float(port_getiri.std(ddof=0) * np.sqrt(AYDA))
    sharpe = float(port_getiri.mean() * AYDA / oyn) if oyn > 0 else float("nan")
    sonuc = Sonuc(
        ad=ad or str(pozisyon.name),
        baslangic=str(fiyat.index[0].date()),
        bitis=str(fiyat.index[-1].date()),
        yil=round(yil, 1),
        cagr=cagr,
        yillik_oynaklik=oyn,
        sharpe_rf0=sharpe,
        max_dusus=_max_dusus(ozkaynak),
        son_deger=float(ozkaynak.iloc[-1]),
        islem_sayisi=int(degisim.sum()),
        piyasada_oran=float(poz_onceki.iloc[1:].mean()) if len(poz_onceki) > 1 else 0.0,
    )
    return ozkaynak.rename(sonuc.ad), sonuc


# ------------------------------------------------------------------ gecikme analizi
def gecikme_analizi(fiyat: pd.Series, pozisyon: pd.Series) -> pd.DataFrame:
    """Her tur (giriş→çıkış) için gecikme maliyetini ölçer.

    - dipten_uzaklik: giriş fiyatı, önceki çıkıştan (ya da seri başından) girişe
      kadar görülen en düşük fiyatın ne kadar üstünde (%). "Dipte alınmadı" ölçüsü.
    - tepeden_uzaklik: çıkış fiyatı, tur içinde görülen en yüksek fiyatın ne kadar
      altında (%). "Tepede satılmadı" ölçüsü.
    - tur_getirisi: çıkış/giriş - 1.
    - disarida_kacirilan: çıkıştan bir sonraki girişe kadar fiyatın değişimi;
      pozitifse dışarıda kalmak para kaybettirdi ("ucuza sattı, pahalıya geri aldı").
    Giriş/çıkış fiyatı sinyal ayının kapanışıdır (pozisyon o kapanışta kurulur).
    """
    poz = pozisyon.reindex(fiyat.index).fillna(0).astype(int)
    degisim = poz.diff().fillna(poz.iloc[0])
    girisler = list(fiyat.index[degisim == 1])
    cikislar = list(fiyat.index[degisim == -1])
    satirlar = []
    onceki_cikis = fiyat.index[0]
    for g in girisler:
        c_adaylar = [c for c in cikislar if c > g]
        c = c_adaylar[0] if c_adaylar else None
        dip = fiyat.loc[onceki_cikis:g].min()
        satir = {
            "giris": g,
            "cikis": c,
            "giris_fiyat": float(fiyat.loc[g]),
            "dipten_uzaklik": float(fiyat.loc[g] / dip - 1),
        }
        if c is not None:
            tepe = fiyat.loc[g:c].max()
            satir.update(
                cikis_fiyat=float(fiyat.loc[c]),
                tepeden_uzaklik=float(1 - fiyat.loc[c] / tepe),
                tur_getirisi=float(fiyat.loc[c] / fiyat.loc[g] - 1),
            )
            sonraki = [x for x in girisler if x > c]
            if sonraki:
                satir["disarida_kacirilan"] = float(fiyat.loc[sonraki[0]] / fiyat.loc[c] - 1)
            onceki_cikis = c
        satirlar.append(satir)
    return pd.DataFrame(satirlar)


def gecikme_ozeti(tablo: pd.DataFrame) -> dict:
    tam = tablo.dropna(subset=["cikis"]) if "cikis" in tablo else tablo.iloc[0:0]
    ozet = {
        "tur_sayisi": int(len(tam)),
        "ort_dipten_uzaklik": float(tablo["dipten_uzaklik"].mean()) if len(tablo) else float("nan"),
        "ort_tepeden_uzaklik": float(tam["tepeden_uzaklik"].mean()) if len(tam) else float("nan"),
        "kazanan_tur_orani": float((tam["tur_getirisi"] > 0).mean()) if len(tam) else float("nan"),
        "medyan_tur_getirisi": float(tam["tur_getirisi"].median()) if len(tam) else float("nan"),
    }
    if "disarida_kacirilan" in tam and tam["disarida_kacirilan"].notna().any():
        d = tam["disarida_kacirilan"].dropna()
        ozet["pahaliya_geri_alma_orani"] = float((d > 0).mean())
        ozet["ort_disarida_kacirilan"] = float(d.mean())
    return ozet


# ------------------------------------------------------------------- ileriye dönük
def ileriye_donuk(
    fiyat: pd.Series,
    adaylar: list[int],
    egitim_ay: int = 360,
    test_ay: int = 120,
    maliyet: float = 0.0,
    nakit_getiri: pd.Series | None = None,
    olcut: str = "cagr",
) -> tuple[pd.DataFrame, pd.Series]:
    """Yürüyen pencere: eğitimde en iyi SMA uzunluğunu seç, sonraki test penceresinde uygula.

    Döner: (pencere tablosu, birleştirilmiş test pozisyon serisi).
    Tablo sütunları: egitim_bas, test_bas, test_bit, secilen_n, egitim_cagr,
    test_cagr_secilen, test_cagr_sma10, test_cagr_al_ve_tut.
    """
    if not adaylar:
        raise ValueError("adaylar boş")
    n_maks = max(adaylar)
    satirlar = []
    poz_birlesik = pd.Series(0, index=fiyat.index, dtype=int)
    bas = 0
    while bas + egitim_ay + test_ay <= len(fiyat):
        egitim = fiyat.iloc[bas : bas + egitim_ay]
        # test penceresi için sinyal hesaplarken HO ısınması için geçmişi dahil et
        test_bas_i = bas + egitim_ay
        test_bit_i = test_bas_i + test_ay
        gecmisli = fiyat.iloc[max(0, test_bas_i - n_maks) : test_bit_i]
        test = fiyat.iloc[test_bas_i:test_bit_i]

        en_iyi_n, en_iyi_skor = None, -np.inf
        for n in adaylar:
            _, s = geri_test(egitim, sma_kurali(egitim, n), maliyet, nakit_getiri, ad=f"sma{n}")
            skor = getattr(s, olcut)
            if np.isfinite(skor) and skor > en_iyi_skor:
                en_iyi_n, en_iyi_skor = n, skor
        assert en_iyi_n is not None

        poz_sec = sma_kurali(gecmisli, en_iyi_n).reindex(test.index)
        poz_10 = sma_kurali(gecmisli, 10).reindex(test.index)
        _, s_sec = geri_test(test, poz_sec, maliyet, nakit_getiri, ad="secilen")
        _, s_10 = geri_test(test, poz_10, maliyet, nakit_getiri, ad="sma10")
        _, s_bh = geri_test(test, al_ve_tut(test), 0.0, None, ad="al_ve_tut")
        poz_birlesik.loc[test.index] = poz_sec.to_numpy()
        satirlar.append(
            {
                "egitim_bas": egitim.index[0].date(),
                "test_bas": test.index[0].date(),
                "test_bit": test.index[-1].date(),
                "secilen_n": en_iyi_n,
                "egitim_cagr": en_iyi_skor,
                "test_cagr_secilen": s_sec.cagr,
                "test_cagr_sma10": s_10.cagr,
                "test_cagr_al_ve_tut": s_bh.cagr,
            }
        )
        bas += test_ay
    return pd.DataFrame(satirlar), poz_birlesik
