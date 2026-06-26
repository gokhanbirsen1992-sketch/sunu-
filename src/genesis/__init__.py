"""Genesis: Çift Katmanlı Evrim (Nested Evolution / Meta-Optimization).

Tanrı (Olimpos) → Evren (fizik kuralları) → Robot (Arena) hiyerarşisiyle
trading stratejilerini evrimleştiren meta-optimizasyon motoru.
"""
from .engine import (
    Deity,
    GenesisConfig,
    GenesisResult,
    run_genesis,
)
from .genome import GodGenome, RobotGenome
from .strategy import EvolvableStrategy

__all__ = [
    "GenesisConfig",
    "GenesisResult",
    "Deity",
    "RobotGenome",
    "GodGenome",
    "EvolvableStrategy",
    "run_genesis",
]
