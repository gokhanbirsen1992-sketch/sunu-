"""Çok varlıklı portföy + rebalans simülasyonu (TL bazlı).

Varlıklar (sentetik, TR karakterine kalibre):
- BIST endeksi: mevcut rejim-değişimli üreteç.
- USD/TL: düşük oynaklıklı sürekli değer kaybı + nadir devalüasyon sıçramaları.
- Altın (TL) = USD/TL × ons altın (USD, GBM).
- Para piyasası / mevduat: sabit günlük bileşik faiz, oynaklık yok.

Karşılaştırılan portföyler:
- %100 BIST al-tut
- Statik karışım (hiç dengelenmez, ağırlıklar sürüklenir)
- Aylık rebalans
- %5 bant rebalansı (ağırlık hedeften 5 puan sapınca dengele — az işlem)
"""
from __future__ import annotations

import numpy as np

from .veri import sentetik_bist


def varliklar_uret(seed: int, n_gun: int = 2520) -> np.ndarray:
    """(n_gun, 4) fiyat matrisi: [BIST, AltınTL, USDTL, ParaPiyasası]."""
    rng = np.random.default_rng(seed + 50_000)
    bist = sentetik_bist(n_gun=n_gun, seed=seed)["close"].to_numpy()
    bist = bist / bist[0]

    # USD/TL: yıllık ~%30 sürüklenme, %8 oynaklık + şok günleri (dalgalanma az, yön tek)
    r_usd = rng.normal(0.30 / 252, 0.08 / np.sqrt(252), n_gun)
    sok = rng.random(n_gun) < 0.004
    r_usd[sok] += rng.uniform(0.03, 0.12, sok.sum())
    usd = np.exp(np.cumsum(r_usd))

    # Ons altın (USD): yıllık ~%6 sürüklenme, %15 oynaklık
    r_ons = rng.normal(0.06 / 252, 0.15 / np.sqrt(252), n_gun)
    altin = usd * np.exp(np.cumsum(r_ons))
    altin = altin / altin[0]
    usd = usd / usd[0]

    # Para piyasası: yıllık ~%35 bileşik, oynaklıksız
    ppf = (1 + 0.35) ** (np.arange(n_gun) / 252.0)

    return np.column_stack([bist, altin, usd, ppf])


def portfoy_sim(
    fiyatlar: np.ndarray,
    hedef: np.ndarray,
    rebalans: str = "aylik",        # "yok" | "aylik" | "bant"
    bant: float = 0.05,
    maliyet: float = 0.001,          # dengelenen tutar üzerinden tek yön ~%0.1
) -> dict:
    n_gun, n_v = fiyatlar.shape
    getiriler = fiyatlar[1:] / fiyatlar[:-1] - 1.0
    deger = np.ones(n_gun)
    pay = hedef.copy()               # portföy değerinin varlıklara dağılımı (oran)
    for t in range(1, n_gun):
        buyume = pay * (1 + getiriler[t - 1])
        deger[t] = deger[t - 1] * buyume.sum()
        pay = buyume / buyume.sum()
        yeniden = False
        if rebalans == "aylik" and t % 21 == 0:
            yeniden = True
        elif rebalans == "bant" and np.abs(pay - hedef).max() > bant:
            yeniden = True
        if yeniden:
            islem_hacmi = np.abs(pay - hedef).sum() / 2.0
            deger[t] *= 1 - islem_hacmi * maliyet * 2.0
            pay = hedef.copy()
    yil = n_gun / 252.0
    tepe = np.maximum.accumulate(deger)
    return {
        "cagr": (deger[-1] ** (1 / yil) - 1) * 100,
        "dd": float((1 - deger / tepe).max() * 100),
        "son": deger[-1],
    }


def karsilastir(seeds=range(10), hedef=(0.40, 0.25, 0.15, 0.20)) -> dict:
    hedef = np.array(hedef)
    sonuclar: dict[str, list] = {"bist": [], "statik": [], "aylik": [], "bant": []}
    for s in seeds:
        f = varliklar_uret(s)
        yil = len(f) / 252.0
        tepe = np.maximum.accumulate(f[:, 0])
        sonuclar["bist"].append(
            {"cagr": (f[-1, 0] ** (1 / yil) - 1) * 100, "dd": float((1 - f[:, 0] / tepe).max() * 100)}
        )
        sonuclar["statik"].append(portfoy_sim(f, hedef, "yok"))
        sonuclar["aylik"].append(portfoy_sim(f, hedef, "aylik"))
        sonuclar["bant"].append(portfoy_sim(f, hedef, "bant"))
    return sonuclar
