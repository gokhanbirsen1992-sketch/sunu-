import numpy as np
import pandas as pd
import pytest

from src.strategies import build_strategy


def _make_df(closes: list[float]) -> pd.DataFrame:
    n = len(closes)
    arr = np.array(closes, dtype=float)
    return pd.DataFrame(
        {
            "timestamp": pd.date_range("2024-01-01", periods=n, freq="1D", tz="UTC"),
            "open": arr,
            "high": arr * 1.01,
            "low": arr * 0.99,
            "close": arr,
            "volume": np.ones(n) * 100.0,
        }
    )


def test_rsi_ma_buy_on_oversold_uptrend():
    # 250 bar uzun yükseliş + son 14 barda sert düşüş → uptrend + oversold
    base = list(np.linspace(100, 300, 250))
    drop = list(np.linspace(300, 250, 14))
    df = _make_df(base + drop)
    strat = build_strategy("rsi_ma", {})
    sig = strat.generate_signal(df, current_price=250.0)
    assert sig.action == "BUY"
    assert sig.indicators["rsi"] < 30


def test_rsi_ma_hold_on_neutral():
    closes = list(np.linspace(100, 200, 250))
    df = _make_df(closes)
    strat = build_strategy("rsi_ma", {})
    sig = strat.generate_signal(df, current_price=200.0)
    assert sig.action == "HOLD"


def test_ma_crossover_buy():
    # uzun yatay (her iki EMA eşit) + ani yukarı sıçrama → kesişim son barda
    flat = [100.0] * 60
    spike = [120.0]
    df = _make_df(flat + spike)
    strat = build_strategy("ma_crossover", {"ema_fast": 5, "ema_slow": 20})
    sig = strat.generate_signal(df, current_price=120.0)
    assert sig.action == "BUY"


def test_unknown_strategy_raises():
    with pytest.raises(ValueError):
        build_strategy("nope", {})


def test_bb_rsi_buy_on_lower_band_oversold():
    # uzun yatay (düşük std) + son barda sert dip → fiyat alt bandın altına düşer
    flat = [100.0] * 40
    crash = [70.0]
    df = _make_df(flat + crash)
    strat = build_strategy("bb_rsi", {})
    sig = strat.generate_signal(df, current_price=70.0)
    assert sig.action == "BUY"
