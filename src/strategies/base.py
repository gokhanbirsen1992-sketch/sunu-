"""Strateji arayüzü."""
from __future__ import annotations

from abc import ABC, abstractmethod

import pandas as pd

from src.signal import Signal


class Strategy(ABC):
    name: str = "base"

    @abstractmethod
    def generate_signal(self, df: pd.DataFrame, current_price: float) -> Signal:
        """`df`: timestamp, open, high, low, close, volume kolonlu DataFrame.
        `current_price`: en güncel ticker fiyatı (henüz kapanmamış mum için).
        """

    def min_bars(self) -> int:
        """Strateji için gerekli minimum bar sayısı."""
        return 200
