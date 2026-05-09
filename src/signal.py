"""Sinyal modeli."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Literal

Action = Literal["BUY", "SELL", "HOLD"]


@dataclass
class Signal:
    action: Action
    price: float
    reason: str
    stop_loss: float | None = None
    take_profit: float | None = None
    suggested_size_usdt: float | None = None
    indicators: dict[str, float] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def is_actionable(self) -> bool:
        return self.action in ("BUY", "SELL")
