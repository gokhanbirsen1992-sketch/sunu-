"""Izgara arama + sağlamlık turnuvası.

Değerlendirme protokolü (aşırı uyum/overfitting'e karşı):
- Eğitim: TRAIN_SEEDS senaryolarında (günlük + haftalık) ızgara arama.
- Sıralama ölçütü: medyan alpha (strateji% - HODL%) - drawdown cezası.
- Doğrulama: kazanan parametreler, hiç görülmemiş TEST_SEEDS senaryolarında
  koşulur; rapor sadece bu out-of-sample sonuçlarla verilir.
"""
from __future__ import annotations

import itertools
import json
from functools import lru_cache

import numpy as np

from .motor import Sonuc, backtest
from .stratejiler import AILELER
from .veri import haftalik, sentetik_bist

TRAIN_SEEDS = list(range(0, 10))
TEST_SEEDS = list(range(100, 115))
KOMISYON = 0.1  # % — BIST aracı kurum ortalaması


@lru_cache(maxsize=256)
def veri_seti(seed: int, hisse_mi: bool = False):
    g = sentetik_bist(seed=seed, hisse_mi=hisse_mi)
    return {"gunluk": g, "haftalik": haftalik(g)}


def kos(aile: str, params: dict, df, bar_per_yil: float) -> Sonuc:
    fn = AILELER[aile]
    o, h, l, c, v = (df[k].to_numpy() for k in ("open", "high", "low", "close", "volume"))
    sinyal, stop = fn(o, h, l, c, v, params)
    return backtest(o, h, l, c, sinyal, KOMISYON, bar_per_yil, stop)


def degerlendir(aile: str, params: dict, seeds: list[int], hisse_mi: bool = False) -> dict:
    """Parametre setini tüm senaryolarda (günlük+haftalık) koşar, özet döndürür."""
    cagr_farklari, dd_farklari, islemler, gecen = [], [], [], 0
    toplam = 0
    detay = []
    for s in seeds:
        vs = veri_seti(s, hisse_mi)
        for tf, bpy in (("gunluk", 252.0), ("haftalik", 52.0)):
            r = kos(aile, params, vs[tf], bpy)
            toplam += 1
            cagr_farklari.append(r.cagr - r.hodl_cagr)
            dd_farklari.append(r.maks_dusus - r.hodl_maks_dusus)
            islemler.append(r.islem_sayisi)
            if r.hodl_gecti_mi():
                gecen += 1
            detay.append(
                {
                    "seed": s, "tf": tf,
                    "net": round(r.net_kar_yuzde, 1), "hodl": round(r.hodl_yuzde, 1),
                    "cagr": round(r.cagr, 1), "hodl_cagr": round(r.hodl_cagr, 1),
                    "dd": round(r.maks_dusus, 1), "hodl_dd": round(r.hodl_maks_dusus, 1),
                    "islem": r.islem_sayisi, "kazanma": round(r.kazanma_orani, 1),
                    "pf": round(r.kar_faktoru, 2) if np.isfinite(r.kar_faktoru) else None,
                }
            )
    med_cagr_fark = float(np.median(cagr_farklari))
    med_dd_fark = float(np.median(dd_farklari))
    # Skor: yıllık getiri avantajı + drawdown azaltma bonusu (DD azalması pozitif katkı)
    skor = med_cagr_fark - 0.25 * med_dd_fark
    if float(np.median(islemler)) < 3:
        skor -= 1000.0  # işlem üretmeyen "sürekli long" çözümleri ele
    return {
        "aile": aile, "params": params, "skor": round(skor, 2),
        "medyan_cagr_fark": round(med_cagr_fark, 2),
        "hodl_gecme_orani": round(gecen / toplam * 100.0, 1),
        "medyan_dd_fark": round(med_dd_fark, 2),
        "medyan_islem": float(np.median(islemler)),
        "detay": detay,
    }


def grid_ara(aile: str, izgara: dict, seeds: list[int] | None = None, hisse_mi: bool = False, en_iyi_n: int = 5) -> list[dict]:
    """izgara: {param_adi: [degerler]}. Skora göre sıralı ilk en_iyi_n sonucu döndürür."""
    seeds = seeds if seeds is not None else TRAIN_SEEDS
    anahtarlar = list(izgara)
    sonuclar = []
    for kombo in itertools.product(*(izgara[k] for k in anahtarlar)):
        params = dict(zip(anahtarlar, kombo))
        r = degerlendir(aile, params, seeds, hisse_mi)
        r.pop("detay")
        sonuclar.append(r)
    sonuclar.sort(key=lambda x: x["skor"], reverse=True)
    return sonuclar[:en_iyi_n]


def rapor_yaz(obj, path: str):
    with open(path, "w") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1, default=str)
