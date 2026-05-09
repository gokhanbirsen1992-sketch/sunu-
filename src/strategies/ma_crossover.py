"""Hareketli ortalama kesişim stratejisi."""
from __future__ import annotations

import pandas as pd

from src.indicators import ema
from src.signal import Signal
from src.strategies.base import Strategy


class MaCrossoverStrategy(Strategy):
    name = "ma_crossover"

    def __init__(self, ema_fast: int = 20, ema_slow: int = 50):
        self.ema_fast = ema_fast
        self.ema_slow = ema_slow

    def min_bars(self) -> int:
        return self.ema_slow + 5

    def generate_signal(self, df: pd.DataFrame, current_price: float) -> Signal:
        close = df["close"].copy()
        close.iloc[-1] = current_price

        ef = ema(close, self.ema_fast)
        es = ema(close, self.ema_slow)

        prev_diff = ef.iloc[-2] - es.iloc[-2]
        cur_diff = ef.iloc[-1] - es.iloc[-1]

        action = "HOLD"
        if prev_diff <= 0 < cur_diff:
            action = "BUY"
            reason = (
                f"Yukarı kesişim: EMA{self.ema_fast}={ef.iloc[-1]:.2f} "
                f"> EMA{self.ema_slow}={es.iloc[-1]:.2f}"
            )
        elif prev_diff >= 0 > cur_diff:
            action = "SELL"
            reason = (
                f"Aşağı kesişim: EMA{self.ema_fast}={ef.iloc[-1]:.2f} "
                f"< EMA{self.ema_slow}={es.iloc[-1]:.2f}"
            )
        else:
            reason = (
                f"Kesişim yok: EMA{self.ema_fast}={ef.iloc[-1]:.2f}, "
                f"EMA{self.ema_slow}={es.iloc[-1]:.2f}"
            )

        return Signal(
            action=action,  # type: ignore[arg-type]
            price=current_price,
            reason=reason,
            indicators={
                f"ema_{self.ema_fast}": float(ef.iloc[-1]),
                f"ema_{self.ema_slow}": float(es.iloc[-1]),
            },
        )
