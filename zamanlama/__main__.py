"""`python -m zamanlama` — raporu üreten komut satırı.

Örnek:
    python -m zamanlama                      # 1871–son, fiyat endeksi, maliyet 0
    python -m zamanlama --bas 1950 --maliyet 0.005 --nakit-faizli
    python -m zamanlama --toplam-getiri      # temettü yeniden yatırımlı endeks
"""

from __future__ import annotations

import argparse

import pandas as pd

from .motor import (
    al_ve_tut,
    dip_tepe_kahini,
    gecikme_analizi,
    gecikme_ozeti,
    geri_test,
    ileriye_donuk,
    kesisim_kurali,
    mukemmel_ongoru,
    nakit_getirisi,
    sma_kurali,
    toplam_getiri_fiyati,
    veri_yukle,
)


def _pct(x: float) -> str:
    return f"{x*100:6.2f}%"


def _tablo(sonuclar) -> str:
    bas = "| Strateji | CAGR | Yıllık oynaklık | Sharpe (rf=0) | Maks. düşüş | 1 birim → | İşlem | Piyasada % |"
    ciz = "|---|---:|---:|---:|---:|---:|---:|---:|"
    satirlar = [bas, ciz]
    for s in sonuclar:
        satirlar.append(
            f"| {s.ad} | {_pct(s.cagr)} | {_pct(s.yillik_oynaklik)} | {s.sharpe_rf0:5.2f} | "
            f"{_pct(s.max_dusus)} | {s.son_deger:,.1f} | {s.islem_sayisi} | {_pct(s.piyasada_oran)} |"
        )
    return "\n".join(satirlar)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--bas", type=int, default=1871, help="başlangıç yılı")
    p.add_argument("--bit", type=int, default=None, help="bitiş yılı (dahil)")
    p.add_argument("--maliyet", type=float, default=0.0, help="tek yön işlem maliyeti (oran, örn. 0.005)")
    p.add_argument("--nakit-faizli", action="store_true", help="nakitteyken 10y faiz/12 kazan (kaba vekil)")
    p.add_argument("--toplam-getiri", action="store_true", help="temettü yeniden yatırımlı endeks kullan")
    p.add_argument("--esik", type=float, default=0.20, help="zigzag kâhini için dönüş eşiği")
    p.add_argument("--egitim-ay", type=int, default=360)
    p.add_argument("--test-ay", type=int, default=120)
    a = p.parse_args(argv)

    df = veri_yukle()
    bit = a.bit if a.bit is not None else df.index[-1].year
    df = df.loc[f"{a.bas}":f"{bit}"]
    fiyat = toplam_getiri_fiyati(df) if a.toplam_getiri else df["fiyat"]
    nakit = nakit_getirisi(df) if a.nakit_faizli else None

    print(f"# Zamanlama geri-testi — {fiyat.index[0].date()} → {fiyat.index[-1].date()}")
    print(
        f"Veri: {'toplam getiri (temettü/12 yeniden yatırım)' if a.toplam_getiri else 'fiyat endeksi (temettüsüz)'}; "
        f"maliyet tek yön {a.maliyet*100:.2f}%; nakit: {'10y faiz/12' if a.nakit_faizli else '0'}\n"
    )
    if a.toplam_getiri:
        son_tem = df["temettu"].dropna().index.max()
        print(f"Uyarı: temettü verisi {son_tem.date()} sonrasında yok; o tarihten sonra yalnızca fiyat getirisi.\n")

    stratejiler = [
        al_ve_tut(fiyat),
        sma_kurali(fiyat, 10),
        sma_kurali(fiyat, 12),
        kesisim_kurali(fiyat, 2, 10),
        kesisim_kurali(fiyat, 3, 12),
        dip_tepe_kahini(fiyat, a.esik),
        mukemmel_ongoru(fiyat),
    ]
    sonuclar = []
    for poz in stratejiler:
        kahin = str(poz.name).startswith("kahin")
        _, s = geri_test(fiyat, poz, a.maliyet, nakit, ad=("KÂHİN " if kahin else "") + str(poz.name))
        sonuclar.append(s)
    print("## Özet\n")
    print(_tablo(sonuclar))
    print("\nKÂHİN satırları gelecek bilgisi kullanır; ulaşılabilir değil, yalnızca üst sınır.\n")

    print("## Gecikme maliyeti (sinyal 'dipte alıyor mu, tepede satıyor mu?')\n")
    print("| Kural | Tur | Girişte dipten uzaklık (ort.) | Çıkışta tepeden uzaklık (ort.) | Kazanan tur % | Pahalıya geri alma % | Dışarıdayken kaçırılan (ort.) |")
    print("|---|---:|---:|---:|---:|---:|---:|")
    for poz in stratejiler[1:5]:
        o = gecikme_ozeti(gecikme_analizi(fiyat, poz))
        print(
            f"| {poz.name} | {o['tur_sayisi']} | {_pct(o['ort_dipten_uzaklik'])} | {_pct(o['ort_tepeden_uzaklik'])} | "
            f"{_pct(o['kazanan_tur_orani'])} | {_pct(o.get('pahaliya_geri_alma_orani', float('nan')))} | "
            f"{_pct(o.get('ort_disarida_kacirilan', float('nan')))} |"
        )
    print()

    print(f"## İleriye dönük (walk-forward) parametre seçimi — eğitim {a.egitim_ay} ay, test {a.test_ay} ay\n")
    adaylar = list(range(2, 25))
    tablo, poz_wf = ileriye_donuk(fiyat, adaylar, a.egitim_ay, a.test_ay, a.maliyet, nakit)
    with pd.option_context("display.float_format", lambda x: f"{x:.4f}", "display.width", 200):
        print(tablo.to_string(index=False))
    if len(tablo):
        ilk = pd.Timestamp(tablo["test_bas"].iloc[0])
        son = pd.Timestamp(tablo["test_bit"].iloc[-1])
        kesit = fiyat.loc[ilk:son]
        _, s_wf = geri_test(kesit, poz_wf.loc[ilk:son], a.maliyet, nakit, ad="wf_secilen")
        _, s_10 = geri_test(kesit, sma_kurali(fiyat, 10).loc[ilk:son], a.maliyet, nakit, ad="sma10_sabit")
        _, s_bh = geri_test(kesit, al_ve_tut(kesit), 0.0, None, ad="al_ve_tut")
        print(f"\nBirleşik test dönemi {ilk.date()} → {son.date()}:\n")
        print(_tablo([s_bh, s_10, s_wf]))
        kazanma = (tablo["test_cagr_secilen"] > tablo["test_cagr_al_ve_tut"]).mean()
        print(f"\nSeçilen parametre test penceresinde al-ve-tut'u geçti: pencerelerin {_pct(kazanma)}")
        print(f"Seçilen n değerleri: {tablo['secilen_n'].tolist()}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
