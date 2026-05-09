"""Bollinger Bands + RSI stratejisi."""
from __future__ import annotations

import pandas as pd

from src.indicators import bollinger, rsi
from src.signal import Signal
from src.strategies.base import Strategy


class BollingerRsiStrategy(Strategy):
    name = "bb_rsi"

    def __init__(
        self,
        bb_period: int = 20,
        bb_std: float = 2.0,
        rsi_period: int = 14,
        rsi_oversold: float = 30,
        rsi_overbought: float = 70,
    ):
        self.bb_period = bb_period
        self.bb_std = bb_std
        self.rsi_period = rsi_period
        self.rsi_oversold = rsi_oversold
        self.rsi_overbought = rsi_overbought

    def min_bars(self) -> int:
        return max(self.bb_period, self.rsi_period) + 5

    def generate_signal(self, df: pd.DataFrame, current_price: float) -> Signal:
        close = df["close"].copy()
        close.iloc[-1] = current_price

        lower, mid, upper = bollinger(close, self.bb_period, self.bb_std)
        rsi_series = rsi(close, self.rsi_period)

        last_close = float(close.iloc[-1])
        last_lower = float(lower.iloc[-1])
        last_upper = float(upper.iloc[-1])
        last_rsi = float(rsi_series.iloc[-1])

        action = "HOLD"
        if last_close <= last_lower and last_rsi < self.rsi_oversold:
            action = "BUY"
            reason = (
                f"Fiyat alt bandın altında ({last_close:.2f}≤{last_lower:.2f}) + "
                f"RSI={last_rsi:.1f} aşırı satım"
            )
        elif last_close >= last_upper and last_rsi > self.rsi_overbought:
            action = "SELL"
            reason = (
                f"Fiyat üst bandın üstünde ({last_close:.2f}≥{last_upper:.2f}) + "
                f"RSI={last_rsi:.1f} aşırı alım"
            )
        else:
            reason = (
                f"BB[{last_lower:.2f},{last_upper:.2f}], RSI={last_rsi:.1f}"
            )

        return Signal(
            action=action,  # type: ignore[arg-type]
            price=current_price,
            reason=reason,
            indicators={
                "bb_lower": last_lower,
                "bb_upper": last_upper,
                "rsi": last_rsi,
            },
        )
