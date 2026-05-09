from src.strategies.base import Strategy
from src.strategies.bb_rsi import BollingerRsiStrategy
from src.strategies.ma_crossover import MaCrossoverStrategy
from src.strategies.rsi_ma import RsiMaStrategy

STRATEGY_REGISTRY: dict[str, type[Strategy]] = {
    "rsi_ma": RsiMaStrategy,
    "ma_crossover": MaCrossoverStrategy,
    "bb_rsi": BollingerRsiStrategy,
}


def build_strategy(name: str, params: dict) -> Strategy:
    if name not in STRATEGY_REGISTRY:
        raise ValueError(
            f"Bilinmeyen strateji: {name!r}. Mevcut: {list(STRATEGY_REGISTRY)}"
        )
    return STRATEGY_REGISTRY[name](**params)


__all__ = ["Strategy", "STRATEGY_REGISTRY", "build_strategy"]
