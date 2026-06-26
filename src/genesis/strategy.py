"""Genomdan üreyen evrimleşebilir strateji.

``EvolvableStrategy`` mevcut ``Strategy`` arayüzünü uygular; böylece evrimin
sonunda kazanan bir robot, hiçbir değişiklik gerektirmeden canlı ``monitor``
veya klasik ``backtest`` komutlarına takılabilir.

Aynı modül, GA fitness değerlendirmesi için tüm barların oy/skorunu tek
seferde üreten *vektörel* yardımcıları da sağlar (``compute_scores``).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from src.indicators import bollinger, ema, rsi
from src.signal import Signal
from src.strategies.base import Strategy

from .genome import GodGenome, RobotGenome


def _macd(close: pd.Series, fast: int, slow: int, signal: int) -> tuple[pd.Series, pd.Series]:
    macd_line = ema(close, fast) - ema(close, slow)
    signal_line = ema(macd_line, signal)
    return macd_line, signal_line


def compute_votes(df: pd.DataFrame, g: RobotGenome) -> dict[str, np.ndarray]:
    """Her indikatör için bar-bazlı oy dizisi (-1/0/+1) döndürür."""
    close = df["close"]

    rsi_v = rsi(close, g.rsi_period)
    rsi_vote = np.where(rsi_v < g.rsi_low, 1.0, np.where(rsi_v > g.rsi_high, -1.0, 0.0))

    ema_f = ema(close, g.ema_fast)
    ema_s = ema(close, g.ema_slow)
    trend_vote = np.where(ema_f > ema_s, 1.0, np.where(ema_f < ema_s, -1.0, 0.0))

    lower, _, upper = bollinger(close, g.bb_period, g.bb_std)
    bb_vote = np.where(close < lower, 1.0, np.where(close > upper, -1.0, 0.0))

    macd_line, signal_line = _macd(close, g.macd_fast, g.macd_slow, g.macd_signal)
    macd_vote = np.where(macd_line > signal_line, 1.0, np.where(macd_line < signal_line, -1.0, 0.0))

    # Isınmamış (NaN) bölgeleri 0 oy yap.
    def clean(series, arr):
        arr = arr.astype(float).copy()
        arr[np.asarray(series.isna())] = 0.0
        return arr

    return {
        "rsi": clean(rsi_v, rsi_vote),
        "trend": clean(ema_s, trend_vote),
        "bb": clean(lower, bb_vote),
        "macd": clean(signal_line, macd_vote),
    }


def compute_scores(df: pd.DataFrame, robot: RobotGenome, god: GodGenome) -> np.ndarray:
    """Tüm barlar için ağırlıklı toplam skoru döndürür (maske uygulanmış)."""
    votes = compute_votes(df, robot)
    score = np.zeros(len(df), dtype=float)
    for ind, vote in votes.items():
        if god.mask.get(ind, 0):
            score += robot.weights.get(ind, 0.0) * vote
    return score


def effective_threshold(robot: RobotGenome, god: GodGenome) -> float:
    """Agresiflik eşiği düşürür: agresif evren daha çok işlem açtırır."""
    return max(0.05, robot.entry_threshold / max(god.aggression, 1e-6))


class EvolvableStrategy(Strategy):
    """Bir ``RobotGenome`` + ``GodGenome`` (evren) çiftinden sinyal üretir."""

    name = "genesis"

    def __init__(self, robot: RobotGenome, god: GodGenome | None = None):
        self.robot = robot
        self.god = god or GodGenome(mask={ind: 1 for ind in robot.weights})
        self._threshold = effective_threshold(self.robot, self.god)

    def min_bars(self) -> int:
        return self.robot.min_bars()

    def generate_signal(self, df: pd.DataFrame, current_price: float) -> Signal:
        scores = compute_scores(df, self.robot, self.god)
        score = float(scores[-1])
        th = self._threshold

        if score >= th:
            action = "BUY"
        elif score <= -th:
            action = "SELL"
        else:
            action = "HOLD"

        reason = (
            f"Genesis skor={score:+.2f} (eşik={th:.2f}); "
            f"evren: {self.god.describe()}"
        )
        return Signal(
            action=action,
            price=current_price,
            reason=reason,
            indicators={"genesis_score": round(score, 3), "threshold": round(th, 3)},
        )


__all__ = [
    "EvolvableStrategy",
    "compute_scores",
    "compute_votes",
    "effective_threshold",
]
