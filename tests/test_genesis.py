"""Genesis çift katmanlı evrim motoru testleri."""
from __future__ import annotations

import random

import numpy as np
import pandas as pd
import pytest

from src.genesis.engine import (
    GenesisConfig,
    evaluate_robot,
    run_genesis,
    simulate,
)
from src.genesis.genome import INDICATORS, GodGenome, RobotGenome
from src.genesis.strategy import EvolvableStrategy, compute_scores, effective_threshold
from src.risk import RiskConfig


def _synthetic_df(n: int = 600, seed: int = 0) -> pd.DataFrame:
    """Trend + gürültü içeren sentetik OHLC verisi (ağ gerekmez)."""
    rng = np.random.default_rng(seed)
    # Rejim değişimi: önce yükseliş, sonra düşüş — out-of-sample anlamlı olsun.
    drift = np.concatenate([np.full(n // 2, 0.002), np.full(n - n // 2, -0.001)])
    rets = drift + rng.normal(0, 0.02, n)
    close = 100 * np.exp(np.cumsum(rets))
    high = close * (1 + np.abs(rng.normal(0, 0.01, n)))
    low = close * (1 - np.abs(rng.normal(0, 0.01, n)))
    open_ = np.concatenate([[close[0]], close[:-1]])
    ts = pd.date_range("2020-01-01", periods=n, freq="D", tz="UTC")
    return pd.DataFrame(
        {"timestamp": ts, "open": open_, "high": high, "low": low, "close": close,
         "volume": rng.uniform(1, 100, n)}
    )


# --------------------------------------------------------------------------- #
# Genom operatörleri
# --------------------------------------------------------------------------- #
def test_robot_random_within_bounds():
    rng = random.Random(1)
    g = RobotGenome.random(rng)
    assert set(g.weights) == set(INDICATORS)
    assert all(-2.0 <= w <= 2.0 for w in g.weights.values())
    assert 5 <= g.rsi_period <= 30
    assert g.min_bars() > 0


def test_god_always_has_active_indicator():
    rng = random.Random(2)
    for _ in range(50):
        g = GodGenome.random(rng, max_leverage=5.0, allow_leverage=True)
        assert g.active_indicators(), "Her evrende en az bir indikatör açık olmalı"


def test_god_leverage_forbidden_when_disallowed():
    rng = random.Random(3)
    for _ in range(20):
        g = GodGenome.random(rng, max_leverage=10.0, allow_leverage=False)
        assert g.leverage == 1.0


def test_mutation_returns_new_valid_genome():
    rng = random.Random(4)
    parent = RobotGenome.random(rng)
    child = parent.mutate(rng, rate=0.5)
    assert all(-2.0 <= w <= 2.0 for w in child.weights.values())
    assert 5 <= child.rsi_period <= 30
    assert 0.2 <= child.entry_threshold <= 1.5


def test_crossover_genes_from_parents():
    rng = random.Random(5)
    a = RobotGenome.random(rng)
    b = RobotGenome.random(rng)
    child = RobotGenome.crossover(a, b, rng)
    for ind in INDICATORS:
        assert child.weights[ind] in (a.weights[ind], b.weights[ind])
    assert child.entry_threshold in (a.entry_threshold, b.entry_threshold)


# --------------------------------------------------------------------------- #
# Strateji / skor
# --------------------------------------------------------------------------- #
def test_mask_zeroes_disabled_indicators():
    df = _synthetic_df(300)
    rng = random.Random(6)
    robot = RobotGenome.random(rng)
    only_rsi = GodGenome(mask={ind: (1 if ind == "rsi" else 0) for ind in INDICATORS})
    scores = compute_scores(df, robot, only_rsi)
    # Skor yalnızca rsi oyundan gelir → |skor| ≤ |rsi ağırlığı|
    assert np.nanmax(np.abs(scores)) <= abs(robot.weights["rsi"]) + 1e-9


def test_aggression_lowers_threshold():
    robot = RobotGenome(weights={i: 1.0 for i in INDICATORS}, entry_threshold=1.0)
    calm = GodGenome(mask={i: 1 for i in INDICATORS}, aggression=0.5)
    wild = GodGenome(mask={i: 1 for i in INDICATORS}, aggression=2.0)
    assert effective_threshold(robot, wild) < effective_threshold(robot, calm)


def test_evolvable_strategy_implements_interface():
    df = _synthetic_df(300)
    rng = random.Random(7)
    strat = EvolvableStrategy(RobotGenome.random(rng))
    sig = strat.generate_signal(df, float(df["close"].iloc[-1]))
    assert sig.action in ("BUY", "SELL", "HOLD")
    assert "genesis_score" in sig.indicators


# --------------------------------------------------------------------------- #
# Simülasyon
# --------------------------------------------------------------------------- #
def test_simulate_leverage_amplifies_returns():
    df = _synthetic_df(400, seed=2)
    risk = RiskConfig()
    from src.genesis.engine import _atr_array

    atr = _atr_array(df, risk.atr_period)
    robot = RobotGenome(
        weights={"trend": 1.5, "rsi": 0.0, "bb": 0.0, "macd": 0.0},
        entry_threshold=0.5,
    )
    mask = {i: 1 for i in INDICATORS}
    scores = compute_scores(df, robot, GodGenome(mask=mask))
    th = 0.5
    r1 = simulate(df, scores, th, atr, risk, leverage=1.0, fee_pct=0.001)
    r3 = simulate(df, scores, th, atr, risk, leverage=3.0, fee_pct=0.001)
    assert r1.num_trades == r3.num_trades  # kaldıraç işlem sayısını değiştirmez
    # Aynı işlemler, kaldıraçla büyütülmüş getiri/risk
    assert abs(r3.return_pct) >= abs(r1.return_pct) - 1e-6


def test_simulate_no_trades_when_threshold_unreachable():
    df = _synthetic_df(300)
    risk = RiskConfig()
    from src.genesis.engine import _atr_array

    atr = _atr_array(df, risk.atr_period)
    scores = np.zeros(len(df))
    res = simulate(df, scores, threshold=1.0, atr_values=atr, risk=risk,
                   leverage=1.0, fee_pct=0.001)
    assert res.num_trades == 0
    assert res.return_pct == 0.0


def test_fitness_penalizes_ruin_and_idle():
    from src.genesis.engine import SimResult

    ruined = SimResult(return_pct=-95, max_drawdown_pct=-99, num_trades=5,
                       win_rate=0.1, ruined=True)
    idle = SimResult(return_pct=0, max_drawdown_pct=0, num_trades=0,
                     win_rate=0, ruined=False)
    good = SimResult(return_pct=40, max_drawdown_pct=-10, num_trades=8,
                     win_rate=0.6, ruined=False)
    assert ruined.fitness() < idle.fitness() < good.fitness()


# --------------------------------------------------------------------------- #
# Uçtan uca evrim
# --------------------------------------------------------------------------- #
def test_run_genesis_end_to_end_and_deterministic():
    df = _synthetic_df(600, seed=3)
    cfg = GenesisConfig(
        god_population=4, god_generations=2,
        robot_population=6, robot_generations=2,
        pantheon_size=3, seed=123,
    )
    risk = RiskConfig()
    r1 = run_genesis(df, cfg, risk)
    r2 = run_genesis(df, cfg, risk)

    assert len(r1.pantheon) == 3
    for d in r1.pantheon:
        assert d.test is not None
        assert d.validation is not None
        assert d.god.active_indicators()
    # Aynı tohum + aynı veri => birebir aynı şampiyon test getirisi
    assert [round(d.test.return_pct, 6) for d in r1.pantheon] == [
        round(d.test.return_pct, 6) for d in r2.pantheon
    ]
    # Pantheon, Tanrıların yargılandığı *doğrulama* fitness'ına göre azalan sıralı
    fits = [d.validation.fitness() for d in r1.pantheon]
    assert fits == sorted(fits, reverse=True)


def test_genesis_three_way_split_is_disjoint_and_ordered():
    """Arena < Doğrulama < Test pencereleri zaman olarak ayrık ve sıralı olmalı."""
    df = _synthetic_df(800, seed=8)
    cfg = GenesisConfig(god_population=3, god_generations=1,
                        robot_population=4, robot_generations=1, pantheon_size=2)
    r = run_genesis(df, cfg, RiskConfig())
    assert r.arena_span[1] <= r.val_span[0]
    assert r.val_span[1] <= r.test_span[0]


def test_run_genesis_rejects_tiny_dataset():
    df = _synthetic_df(30)
    cfg = GenesisConfig(god_population=2, god_generations=1,
                        robot_population=2, robot_generations=1)
    with pytest.raises(ValueError):
        run_genesis(df, cfg, RiskConfig())
