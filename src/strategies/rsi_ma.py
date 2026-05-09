"""RSI + EMA crossover stratejisi."""
from __future__ import annotations

import pandas as pd

from src.indicators import ema, rsi
from src.signal import Signal
from src.strategies.base import Strategy


class RsiMaStrategy(Strategy):
    name = "rsi_ma"

    def __init__(
        self,
        rsi_period: int = 14,
        rsi_oversold: float = 30,
        rsi_overbought: float = 70,
        ema_fast: int = 50,
        ema_slow: int = 200,
    ):
        self.rsi_period = rsi_period
        self.rsi_oversold = rsi_oversold
        self.rsi_overbought = rsi_overbought
        self.ema_fast = ema_fast
        self.ema_slow = ema_slow

    def min_bars(self) -> int:
        return self.ema_slow + 5

    def generate_signal(self, df: pd.DataFrame, current_price: float) -> Signal:
        close = df["close"].copy()
        close.iloc[-1] = current_price  # canlı fiyatı son bara yansıt

        rsi_series = rsi(close, self.rsi_period)
        ef = ema(close, self.ema_fast)
        es = ema(close, self.ema_slow)

        last_rsi = float(rsi_series.iloc[-1])
        last_ef = float(ef.iloc[-1])
        last_es = float(es.iloc[-1])

        uptrend = last_ef > last_es
        downtrend = last_ef < last_es

        action: str = "HOLD"
        reason = (
            f"RSI={last_rsi:.1f}, EMA{self.ema_fast}={last_ef:.2f}, "
            f"EMA{self.ema_slow}={last_es:.2f}"
        )

        if uptrend and last_rsi < self.rsi_oversold:
            action = "BUY"
            reason = (
                f"Yükseliş trendi (EMA{self.ema_fast}>EMA{self.ema_slow}) + "
                f"RSI={last_rsi:.1f} aşırı satım"
            )
        elif downtrend and last_rsi > self.rsi_overbought:
            action = "SELL"
            reason = (
                f"Düşüş trendi (EMA{self.ema_fast}<EMA{self.ema_slow}) + "
                f"RSI={last_rsi:.1f} aşırı alım"
            )

        return Signal(
            action=action,  # type: ignore[arg-type]
            price=current_price,
            reason=reason,
            indicators={
                "rsi": last_rsi,
                f"ema_{self.ema_fast}": last_ef,
                f"ema_{self.ema_slow}": last_es,
            },
        )
