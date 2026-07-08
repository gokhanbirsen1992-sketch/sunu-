"""Performans ölçütleri + veri-madenciliği karşıtı istatistikler.

Deflated Sharpe Ratio (DSR) Bailey & López de Prado (2014) formülünü uygular;
``bootstrap_p`` White (2000) Reality Check ruhunda basitleştirilmiş bir blok
bootstrap p-değeridir. Ayrıntı ve gerekçe için bkz. ``alsat/LITERATUR.md`` §4.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats

YILLIK_GUN = 365
RANDOM_STATE = 42


def yillik_getiri(net: pd.Series) -> float:
    if len(net) == 0:
        return 0.0
    buyume = float((1 + net).prod())
    if buyume <= 0:
        return -1.0
    return buyume ** (YILLIK_GUN / len(net)) - 1


def sharpe(net: pd.Series) -> float:
    s = float(net.std())
    if s == 0 or np.isnan(s):
        return 0.0
    return float(net.mean() / s * np.sqrt(YILLIK_GUN))


def sortino(net: pd.Series) -> float:
    asagi = net[net < 0]
    s = float(asagi.std())
    if s == 0 or np.isnan(s):
        return 0.0
    return float(net.mean() / s * np.sqrt(YILLIK_GUN))


def maks_dusus(ozsermaye: pd.Series) -> float:
    """En derin tepe→dip düşüşü (negatif oran, ör. -0.55 = %55 düşüş)."""
    zirve = ozsermaye.cummax()
    return float((ozsermaye / zirve - 1).min())


def isabet_orani(net: pd.Series) -> float:
    aktif = net[net != 0]
    if len(aktif) == 0:
        return 0.0
    return float((aktif > 0).mean())


def deflated_sharpe(net: pd.Series, n_deneme: int,
                    deneme_sharpe_std: float | None = None) -> float:
    """Bailey & López de Prado (2014) DSR: N deneme içinden seçilmiş en iyi
    Sharpe'ın şanstan ayırt edilebilme olasılığı (0-1; >0.5 kayda değer,
    >0.95 güçlü). Çarpıklık/basıklık düzeltmesi dahil."""
    T = len(net)
    if T < 30:
        return 0.0
    sr_gunluk = float(net.mean() / net.std()) if net.std() > 0 else 0.0
    carpiklik = float(stats.skew(net, bias=False))
    basiklik = float(stats.kurtosis(net, fisher=False, bias=False))
    n = max(int(n_deneme), 1)
    # Denemeler arası Sharpe std'si: mümkünse aday tablosundan ampirik olarak verilir
    # (Bailey-LdP 2014'ün öngördüğü budur); yoksa muhafazakâr varsayım: gözlenen
    # SR'nin yarısı.
    std_sr = deneme_sharpe_std if deneme_sharpe_std else max(abs(sr_gunluk) * 0.5, 1e-9)
    std_sr = max(std_sr, 1e-9)
    gama = 0.5772156649015329
    if n > 1:
        z1 = stats.norm.ppf(1 - 1.0 / n)
        z2 = stats.norm.ppf(1 - 1.0 / (n * np.e))
        sr_esik = std_sr * ((1 - gama) * z1 + gama * z2)
    else:
        sr_esik = 0.0
    pay = (sr_gunluk - sr_esik) * np.sqrt(T - 1)
    payda = np.sqrt(max(1 - carpiklik * sr_gunluk + (basiklik - 1) / 4 * sr_gunluk ** 2, 1e-9))
    return float(stats.norm.cdf(pay / payda))


def bootstrap_p(net: pd.Series, n_tekrar: int = 1000, blok: int = 20,
                seed: int = RANDOM_STATE) -> float:
    """H0: ortalama net getiri ≤ 0. Dairesel blok bootstrap (White 2000 ruhunda,
    basitleştirilmiş): sıfır-ortalanmış seriden bloklarla yeniden örneklenen
    ortalamaların, gözlenen ortalamayı aşma sıklığı."""
    x = net.to_numpy()
    T = len(x)
    if T < 60:
        return 1.0
    gozlenen = x.mean()
    merkezli = x - gozlenen
    rng = np.random.default_rng(seed)
    n_blok = int(np.ceil(T / blok))
    baslangiclar = rng.integers(0, T, size=(n_tekrar, n_blok))
    ofset = np.arange(blok)
    indeksler = (baslangiclar[:, :, None] + ofset[None, None, :]) % T
    ornekler = merkezli[indeksler].reshape(n_tekrar, -1)[:, :T]
    return float((ornekler.mean(axis=1) >= gozlenen).mean())


def olcut_tablosu(net: pd.Series, ozsermaye: pd.Series, devir: float,
                  poz_orani: float, n_deneme: int = 1,
                  deneme_sharpe_std: float | None = None) -> dict:
    """Tek dönem için tüm ölçütleri tek sözlükte toplar."""
    return {
        "yillik_getiri": yillik_getiri(net),
        "sharpe": sharpe(net),
        "sortino": sortino(net),
        "maks_dusus": maks_dusus(ozsermaye),
        "isabet": isabet_orani(net),
        "devir": devir,
        "poz_orani": poz_orani,
        "dsr": deflated_sharpe(net, n_deneme, deneme_sharpe_std),
        "bootstrap_p": bootstrap_p(net),
    }
