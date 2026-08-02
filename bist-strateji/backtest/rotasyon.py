"""Kesitsel momentum rotasyonu backtest (Jegadeesh-Titman 1993).

Evren: N hisse. Her rebalans döneminde momentum = C[t-atla] / C[t-uzun-atla] - 1
ile sıralanır; mutlak filtre açıksa yalnızca momentum > 0 olanlardan ilk K hisse
eşit ağırlıkla tutulur (boş kalan slot nakit, %0 getiri). Sinyal rebalans barı
kapanışında; yeni portföy ERTESİ bardan itibaren getiri işler (bakış sızıntısı yok).
Komisyon her değişen bacakta iki yönlü uygulanır.
Kıyas: aynı evrenin eşit ağırlıklı al-ve-tut portföyü.
"""
from __future__ import annotations

import numpy as np

from .veri import sentetik_bist


def rotasyon_backtest(
    fiyatlar: np.ndarray,          # (n_gun, n_hisse) kapanışlar
    uzun: int = 126,
    atla: int = 21,
    top_k: int = 5,
    rebalans_gun: int = 21,
    komisyon_yuzde: float = 0.1,
    mutlak_filtre: bool = True,
) -> dict:
    n_gun, n_hisse = fiyatlar.shape
    kom = komisyon_yuzde / 100.0
    getiriler = fiyatlar[1:] / fiyatlar[:-1] - 1.0     # (n_gun-1, n_hisse)

    equity = np.ones(n_gun)
    tutulan: set[int] = set()
    rotasyon_sayisi = 0
    baslangic = uzun + atla + 1

    for t in range(1, n_gun):
        # 1) Önceki gün belirlenmiş portföyün bugünkü getirisi (boş slot = nakit)
        if tutulan:
            gunluk = np.mean([getiriler[t - 1, i] for i in tutulan]) * len(tutulan) / top_k
        else:
            gunluk = 0.0
        equity[t] = equity[t - 1] * (1.0 + gunluk)

        # 2) Rebalans günü kapanışında yeni seçim (ertesi gün geçerli)
        if t >= baslangic and (t - baslangic) % rebalans_gun == 0:
            mom = fiyatlar[t - atla] / fiyatlar[t - uzun - atla] - 1.0
            sira = np.argsort(-mom)
            yeni = []
            for i in sira:
                if len(yeni) >= top_k:
                    break
                if mutlak_filtre and mom[i] <= 0:
                    break  # sıralı liste — ilk negatifte dur
                yeni.append(int(i))
            yeni_set = set(yeni)
            degisen = len(tutulan ^ yeni_set)
            if degisen:
                # her değişen bacak: sat + al ≈ 2 komisyon, portföy ağırlığıyla
                equity[t] *= 1.0 - degisen * 2.0 * kom / (2.0 * top_k)
                rotasyon_sayisi += 1
            tutulan = yeni_set

    hodl = np.mean(fiyatlar / fiyatlar[0], axis=1)     # eşit ağırlık al-ve-tut
    yil = n_gun / 252.0

    def _cagr(eq):
        return (eq[-1] ** (1.0 / yil) - 1.0) * 100.0

    def _dd(eq):
        tepe = np.maximum.accumulate(eq)
        return float((1.0 - eq / tepe).max() * 100.0)

    return {
        "net": (equity[-1] - 1.0) * 100.0,
        "hodl": (hodl[-1] - 1.0) * 100.0,
        "cagr": _cagr(equity),
        "hodl_cagr": _cagr(hodl),
        "dd": _dd(equity),
        "hodl_dd": _dd(hodl),
        "rotasyon": rotasyon_sayisi,
        "equity": equity,
    }


def evren_uret(seed0: int, n_hisse: int = 20, n_gun: int = 2520) -> np.ndarray:
    return np.column_stack(
        [sentetik_bist(n_gun=n_gun, seed=seed0 + i, hisse_mi=True)["close"].to_numpy() for i in range(n_hisse)]
    )
