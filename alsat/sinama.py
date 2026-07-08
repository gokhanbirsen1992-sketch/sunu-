"""Backtest motoru — kesinlikle nedensel, maliyet dahil, walk-forward.

Nedensellik garantisi: ``backtest`` hedef pozisyonu getiriye uygularken bir gün
kaydırır (``shift(1)``); t günü kapanışında üretilen sinyal en erken t+1 günü
getirisini yakalar. İşlem maliyeti + kayma, pozisyon değişiminin mutlak değeri
üzerinden baz puan (bps) olarak düşülür.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd

VARSAYILAN_MALIYET_BPS = 20.0  # %0.20 tek yön (komisyon + kayma; Han ve ark. 2023 ruhunda)


@dataclass
class SinamaSonucu:
    """Tek bir pozisyon serisinin tek bir dönemdeki backtest çıktısı."""

    net_getiriler: pd.Series          # günlük net getiri
    ozsermaye: pd.Series              # kümülatif özsermaye eğrisi (1'den başlar)
    devir: float                      # toplam |pozisyon değişimi| (işlem yoğunluğu)
    poz_orani: float                  # pozisyonda geçirilen gün oranı
    ekler: dict = field(default_factory=dict)


def backtest(kapanis: pd.Series, pozisyon: pd.Series,
             maliyet_bps: float = VARSAYILAN_MALIYET_BPS) -> SinamaSonucu:
    """Pozisyon serisini bir gün gecikmeyle uygular, maliyeti düşer."""
    getiri = kapanis.pct_change().fillna(0.0)
    uygulanan = pozisyon.reindex(kapanis.index).fillna(0.0).shift(1).fillna(0.0)
    degisim = uygulanan.diff().abs().fillna(uygulanan.abs())
    maliyet = degisim * (maliyet_bps / 1e4)
    net = uygulanan * getiri - maliyet
    ozsermaye = (1 + net).cumprod()
    return SinamaSonucu(
        net_getiriler=net,
        ozsermaye=ozsermaye,
        devir=float(degisim.sum()),
        poz_orani=float((uygulanan > 0).mean()),
    )


def satin_al_tut(kapanis: pd.Series) -> SinamaSonucu:
    """Kıyas: ilk gün al, hiç satma (maliyeti ihmal edilebilir tek işlem)."""
    poz = pd.Series(1.0, index=kapanis.index)
    return backtest(kapanis, poz, maliyet_bps=0.0)


def walk_forward_dilimleri(index: pd.DatetimeIndex, egitim_yil: int = 3,
                           test_yil: int = 1) -> list[tuple[slice, slice]]:
    """Genişleyen pencereli walk-forward dilimleri.

    Eğitim: başlangıçtan test penceresinin başına kadar (en az ``egitim_yil`` yıl);
    test: onu izleyen ``test_yil`` yıllık blok. Test blokları örtüşmez ve tüm
    seri sonuna kadar art arda dizilir.
    """
    baslangic, bitis = index[0], index[-1]
    dilimler: list[tuple[slice, slice]] = []
    test_basi = baslangic + pd.DateOffset(years=egitim_yil)
    while test_basi < bitis:
        test_sonu = min(test_basi + pd.DateOffset(years=test_yil), bitis + pd.Timedelta(days=1))
        dilimler.append((
            slice(baslangic, test_basi - pd.Timedelta(days=1)),
            slice(test_basi, test_sonu - pd.Timedelta(days=1)),
        ))
        test_basi = test_sonu
    if not dilimler:
        raise ValueError(f"Walk-forward için seri çok kısa: {baslangic} → {bitis}")
    return dilimler
