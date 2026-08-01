"""Backtest motoru — TradingView strategy() davranışıyla uyumlu.

Kurallar:
- Sinyal bar kapanışında üretilir, emir BİR SONRAKİ barın açılışında dolar
  (Pine varsayılanı: process_orders_on_close=false).
- Long/flat sistem (BIST'te açığa satış varsayılmaz).
- Komisyon her işlem bacağında yüzde olarak düşülür (alış + satış).
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np


@dataclass
class Sonuc:
    """Backtest çıktı istatistikleri. Getiriler yüzde (%) cinsindendir."""

    net_kar_yuzde: float = 0.0
    hodl_yuzde: float = 0.0
    alpha_yuzde: float = 0.0          # strateji - HODL (yüzde puan)
    islem_sayisi: int = 0
    kazanma_orani: float = 0.0        # % kazanan işlem
    kar_faktoru: float = float("nan")  # brüt kar / brüt zarar
    maks_dusus: float = 0.0           # strateji maks. drawdown %
    hodl_maks_dusus: float = 0.0
    ort_islem_yuzde: float = 0.0
    cagr: float = 0.0
    hodl_cagr: float = 0.0
    sharpe: float = 0.0               # yıllıklandırılmış, rf=0
    equity: np.ndarray = field(default_factory=lambda: np.array([]), repr=False)
    hodl_equity: np.ndarray = field(default_factory=lambda: np.array([]), repr=False)
    islemler: list = field(default_factory=list, repr=False)

    def hodl_gecti_mi(self) -> bool:
        return self.net_kar_yuzde > self.hodl_yuzde


def _max_drawdown(eq: np.ndarray) -> float:
    peak = np.maximum.accumulate(eq)
    dd = (eq - peak) / peak
    return float(-dd.min() * 100.0)


def backtest(
    open_: np.ndarray,
    high: np.ndarray,
    low: np.ndarray,
    close: np.ndarray,
    sinyal: np.ndarray,
    komisyon_yuzde: float = 0.1,
    bar_per_yil: float = 252.0,
    stop_seviyesi: np.ndarray | None = None,
) -> Sonuc:
    """sinyal[i]: i barının KAPANIŞINDA istenen pozisyon (1=long, 0=flat).

    Gerçekleşme i+1 barının açılışında olur. stop_seviyesi verilirse ve bar
    içinde low bu seviyenin altına inerse pozisyon aynı barda stop fiyatından
    (gap varsa açılıştan) kapatılır.
    """
    n = len(close)
    assert len(open_) == len(high) == len(low) == n == len(sinyal)
    kom = komisyon_yuzde / 100.0

    cash = 1.0
    shares = 0.0
    pos = 0
    entry_px = np.nan
    equity = np.zeros(n)
    trades: list[dict] = []

    for i in range(n):
        # 1) Önceki barın sinyalini bu barın açılışında uygula
        istenen = int(sinyal[i - 1]) if i > 0 and not np.isnan(sinyal[i - 1]) else pos
        if istenen != pos:
            px = open_[i]
            if istenen == 1 and pos == 0:
                shares = cash * (1 - kom) / px
                cash = 0.0
                pos = 1
                entry_px = px
                trades.append({"giris_i": i, "giris_px": px})
            elif istenen == 0 and pos == 1:
                cash = shares * px * (1 - kom)
                shares = 0.0
                pos = 0
                trades[-1].update({"cikis_i": i, "cikis_px": px})
                trades[-1]["getiri"] = (px * (1 - kom)) / (entry_px / (1 - kom)) - 1.0
        # 2) Bar içi stop kontrolü (pozisyondayken)
        if pos == 1 and stop_seviyesi is not None and not np.isnan(stop_seviyesi[i]):
            stp = stop_seviyesi[i]
            if low[i] <= stp:
                px = min(open_[i], stp) if open_[i] < stp else stp
                cash = shares * px * (1 - kom)
                shares = 0.0
                pos = 0
                trades[-1].update({"cikis_i": i, "cikis_px": px, "stop": True})
                trades[-1]["getiri"] = (px * (1 - kom)) / (entry_px / (1 - kom)) - 1.0
        equity[i] = cash + shares * close[i]

    # Açık pozisyonu son kapanışta değerle (kapatılmış sayma)
    if pos == 1 and trades and "cikis_i" not in trades[-1]:
        trades[-1].update({"cikis_i": n - 1, "cikis_px": close[-1], "acik": True})
        trades[-1]["getiri"] = (close[-1] * (1 - kom)) / (entry_px / (1 - kom)) - 1.0

    hodl_equity = close / close[0]

    r = Sonuc()
    r.equity = equity
    r.hodl_equity = hodl_equity
    r.islemler = trades
    r.net_kar_yuzde = float((equity[-1] - 1.0) * 100.0)
    r.hodl_yuzde = float((hodl_equity[-1] - 1.0) * 100.0)
    r.alpha_yuzde = r.net_kar_yuzde - r.hodl_yuzde
    r.islem_sayisi = len(trades)
    getiriler = np.array([t["getiri"] for t in trades]) if trades else np.array([])
    if len(getiriler):
        r.kazanma_orani = float((getiriler > 0).mean() * 100.0)
        brut_kar = getiriler[getiriler > 0].sum()
        brut_zarar = -getiriler[getiriler < 0].sum()
        r.kar_faktoru = float(brut_kar / brut_zarar) if brut_zarar > 0 else float("inf")
        r.ort_islem_yuzde = float(getiriler.mean() * 100.0)
    r.maks_dusus = _max_drawdown(equity)
    r.hodl_maks_dusus = _max_drawdown(hodl_equity)
    yil = n / bar_per_yil
    if yil > 0 and equity[-1] > 0:
        r.cagr = float((equity[-1] ** (1.0 / yil) - 1.0) * 100.0)
        r.hodl_cagr = float((hodl_equity[-1] ** (1.0 / yil) - 1.0) * 100.0)
    gunluk = np.diff(equity) / equity[:-1]
    if gunluk.std() > 0:
        r.sharpe = float(gunluk.mean() / gunluk.std() * np.sqrt(bar_per_yil))
    return r
