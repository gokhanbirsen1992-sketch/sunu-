import numpy as np
import pandas as pd
import pytest

from src.backtest import run_backtest
from src.strategies import build_strategy


def _synthetic_df(n: int = 400, seed: int = 0) -> pd.DataFrame:
    rng = np.random.RandomState(seed)
    # rastgele yürüyüş + hafif yükseliş eğilimi
    rets = rng.normal(0.001, 0.02, n)
    close = 100 * np.exp(np.cumsum(rets))
    high = close * (1 + np.abs(rng.normal(0, 0.005, n)))
    low = close * (1 - np.abs(rng.normal(0, 0.005, n)))
    open_ = np.r_[close[0], close[:-1]]
    return pd.DataFrame(
        {
            "timestamp": pd.date_range("2023-01-01", periods=n, freq="1D", tz="UTC"),
            "open": open_,
            "high": high,
            "low": low,
            "close": close,
            "volume": np.ones(n) * 1000,
        }
    )


def test_backtest_runs_and_produces_summary():
    df = _synthetic_df(400, seed=42)
    strat = build_strategy("rsi_ma", {"ema_fast": 50, "ema_slow": 200})
    result = run_backtest(df, strat)
    summary = result.summary()
    assert "total_trades" in summary
    assert "win_rate_pct" in summary
    assert "total_return_pct" in summary
    assert summary["total_trades"] >= 0
    assert len(result.equity_curve) > 0


def test_backtest_rejects_short_data():
    df = _synthetic_df(50)
    strat = build_strategy("rsi_ma", {})
    with pytest.raises(ValueError):
        run_backtest(df, strat)


def test_backtest_ma_crossover_generates_trades():
    df = _synthetic_df(300, seed=1)
    strat = build_strategy("ma_crossover", {"ema_fast": 10, "ema_slow": 30})
    result = run_backtest(df, strat)
    # MA crossover oynak veride en az birkaç işlem üretmeli
    assert result.total_trades > 0
