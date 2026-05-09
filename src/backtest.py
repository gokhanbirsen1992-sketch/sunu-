"""Basit backtest motoru — tek pozisyon, SL/TP destekli."""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime

import pandas as pd

from src.indicators import atr
from src.risk import RiskConfig, compute_sl_tp
from src.strategies.base import Strategy


@dataclass
class Trade:
    side: str
    entry_time: datetime
    entry_price: float
    exit_time: datetime
    exit_price: float
    pnl_pct: float
    exit_reason: str  # "SL", "TP", "SIGNAL"


@dataclass
class BacktestResult:
    trades: list[Trade] = field(default_factory=list)
    equity_curve: list[float] = field(default_factory=list)

    @property
    def total_trades(self) -> int:
        return len(self.trades)

    @property
    def wins(self) -> int:
        return sum(1 for t in self.trades if t.pnl_pct > 0)

    @property
    def losses(self) -> int:
        return sum(1 for t in self.trades if t.pnl_pct <= 0)

    @property
    def win_rate(self) -> float:
        return (self.wins / self.total_trades) if self.total_trades else 0.0

    @property
    def total_return_pct(self) -> float:
        if not self.equity_curve:
            return 0.0
        return (self.equity_curve[-1] / self.equity_curve[0] - 1.0) * 100.0

    @property
    def max_drawdown_pct(self) -> float:
        if not self.equity_curve:
            return 0.0
        peak = self.equity_curve[0]
        dd = 0.0
        for v in self.equity_curve:
            peak = max(peak, v)
            dd = min(dd, (v / peak - 1.0))
        return dd * 100.0

    def summary(self) -> dict[str, float | int]:
        return {
            "total_trades": self.total_trades,
            "wins": self.wins,
            "losses": self.losses,
            "win_rate_pct": round(self.win_rate * 100, 2),
            "total_return_pct": round(self.total_return_pct, 2),
            "max_drawdown_pct": round(self.max_drawdown_pct, 2),
        }


def run_backtest(
    df: pd.DataFrame,
    strategy: Strategy,
    risk: RiskConfig | None = None,
    fee_pct: float = 0.001,  # taraf başına %0.1
) -> BacktestResult:
    """Geçmiş mum verisi üzerinde stratejiyi çalıştır.

    Her bar kapanışında stratejiyi çağırır. Açık pozisyon varken bir sonraki
    barın yüksek/düşük seviyeleri SL/TP'yi tetikleyebilir; aksi takdirde ters
    sinyalde çıkılır. Gerçekçilik için her giriş/çıkış komisyonu uygulanır.
    """
    risk = risk or RiskConfig()
    min_bars = strategy.min_bars()
    if len(df) <= min_bars + 1:
        raise ValueError(
            f"Yetersiz veri: {len(df)} bar, en az {min_bars + 2} gerekli"
        )

    df = df.reset_index(drop=True)
    atr_series = atr(df["high"], df["low"], df["close"], risk.atr_period)

    result = BacktestResult()
    equity = 1.0  # normalize
    result.equity_curve.append(equity)

    position: dict | None = None  # {'side','entry_price','sl','tp','entry_time'}

    for i in range(min_bars, len(df) - 1):
        cur_close = float(df.at[i, "close"])
        next_bar = df.iloc[i + 1]
        next_high = float(next_bar["high"])
        next_low = float(next_bar["low"])
        next_time = next_bar["timestamp"]

        # 1) Açık pozisyon varsa, sonraki bar SL/TP tetikledi mi?
        if position is not None:
            side = position["side"]
            sl = position["sl"]
            tp = position["tp"]
            exit_price = None
            exit_reason = None
            if side == "BUY":
                if next_low <= sl:
                    exit_price, exit_reason = sl, "SL"
                elif next_high >= tp:
                    exit_price, exit_reason = tp, "TP"
            else:  # SELL
                if next_high >= sl:
                    exit_price, exit_reason = sl, "SL"
                elif next_low <= tp:
                    exit_price, exit_reason = tp, "TP"

            if exit_price is not None:
                pnl_pct = _pnl_pct(side, position["entry_price"], exit_price, fee_pct)
                equity *= 1 + pnl_pct
                result.trades.append(
                    Trade(
                        side=side,
                        entry_time=position["entry_time"],
                        entry_price=position["entry_price"],
                        exit_time=next_time,
                        exit_price=exit_price,
                        pnl_pct=pnl_pct * 100,
                        exit_reason=exit_reason,
                    )
                )
                position = None

        # 2) Sinyal üret (cur_close ile)
        slice_df = df.iloc[: i + 1]
        signal = strategy.generate_signal(slice_df, cur_close)

        # 3) Pozisyon yönetimi: ters sinyalde kapat, yoksa aç
        if position is not None and signal.action in ("BUY", "SELL"):
            if signal.action != position["side"]:
                pnl_pct = _pnl_pct(
                    position["side"], position["entry_price"], cur_close, fee_pct
                )
                equity *= 1 + pnl_pct
                result.trades.append(
                    Trade(
                        side=position["side"],
                        entry_time=position["entry_time"],
                        entry_price=position["entry_price"],
                        exit_time=df.at[i, "timestamp"],
                        exit_price=cur_close,
                        pnl_pct=pnl_pct * 100,
                        exit_reason="SIGNAL",
                    )
                )
                position = None

        if position is None and signal.action in ("BUY", "SELL"):
            atr_val = atr_series.iloc[i]
            atr_val = float(atr_val) if not math.isnan(atr_val) else None
            sl, tp = compute_sl_tp(cur_close, signal.action, atr_val, risk)
            position = {
                "side": signal.action,
                "entry_price": cur_close,
                "sl": sl,
                "tp": tp,
                "entry_time": df.at[i, "timestamp"],
            }

        result.equity_curve.append(equity)

    # son pozisyonu kapat
    if position is not None:
        last_close = float(df["close"].iloc[-1])
        pnl_pct = _pnl_pct(position["side"], position["entry_price"], last_close, fee_pct)
        equity *= 1 + pnl_pct
        result.trades.append(
            Trade(
                side=position["side"],
                entry_time=position["entry_time"],
                entry_price=position["entry_price"],
                exit_time=df["timestamp"].iloc[-1],
                exit_price=last_close,
                pnl_pct=pnl_pct * 100,
                exit_reason="SIGNAL",
            )
        )
        result.equity_curve.append(equity)

    return result


def _pnl_pct(side: str, entry: float, exit_p: float, fee_pct: float) -> float:
    """Komisyon dahil yüzde getiri (ondalık olarak)."""
    raw = (exit_p / entry - 1.0) if side == "BUY" else (entry / exit_p - 1.0)
    return raw - 2 * fee_pct
