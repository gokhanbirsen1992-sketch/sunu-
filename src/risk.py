"""Risk yönetimi: stop-loss, take-profit, pozisyon büyüklüğü."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


@dataclass
class RiskConfig:
    equity_usdt: float = 1000.0
    risk_pct: float = 0.01
    atr_period: int = 14
    atr_sl_mult: float = 2.0
    atr_tp_mult: float = 4.0
    fallback_sl_pct: float = 0.02  # ATR yoksa %2

    def __post_init__(self) -> None:
        if self.risk_pct <= 0 or self.risk_pct > 0.5:
            raise ValueError("risk_pct (0, 0.5] aralığında olmalı")
        if self.equity_usdt <= 0:
            raise ValueError("equity_usdt > 0 olmalı")


def compute_sl_tp(
    price: float,
    side: Literal["BUY", "SELL"],
    atr_value: float | None,
    cfg: RiskConfig,
) -> tuple[float, float]:
    """Stop-loss ve take-profit seviyelerini hesapla."""
    if atr_value and atr_value > 0:
        sl_dist = cfg.atr_sl_mult * atr_value
        tp_dist = cfg.atr_tp_mult * atr_value
    else:
        sl_dist = price * cfg.fallback_sl_pct
        tp_dist = price * cfg.fallback_sl_pct * (cfg.atr_tp_mult / cfg.atr_sl_mult)

    if side == "BUY":
        return price - sl_dist, price + tp_dist
    return price + sl_dist, price - tp_dist


def position_size_usdt(price: float, stop_loss: float, cfg: RiskConfig) -> float:
    """Risk yüzdesine göre önerilen pozisyon büyüklüğü (USDT cinsinden)."""
    sl_distance = abs(price - stop_loss)
    if sl_distance <= 0:
        return 0.0
    risk_usdt = cfg.equity_usdt * cfg.risk_pct
    coin_size = risk_usdt / sl_distance
    notional = coin_size * price
    # Maks. equity'nin tamamı (kaldıraç yok)
    return min(notional, cfg.equity_usdt)
