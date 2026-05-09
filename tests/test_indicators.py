import numpy as np
import pandas as pd
import pytest

from src.indicators import atr, bollinger, ema, rsi, sma


def test_sma_basic():
    s = pd.Series([1.0, 2.0, 3.0, 4.0, 5.0])
    out = sma(s, 3)
    assert out.iloc[0:2].isna().all()
    assert out.iloc[2] == pytest.approx(2.0)
    assert out.iloc[4] == pytest.approx(4.0)


def test_ema_converges_to_constant():
    s = pd.Series([10.0] * 50)
    out = ema(s, 10)
    assert out.dropna().iloc[-1] == pytest.approx(10.0)


def test_rsi_monotonically_increasing_is_overbought():
    s = pd.Series(np.arange(1, 101, dtype=float))
    out = rsi(s, 14)
    assert out.iloc[-1] > 70


def test_rsi_monotonically_decreasing_is_oversold():
    s = pd.Series(np.arange(100, 0, -1, dtype=float))
    out = rsi(s, 14)
    assert out.iloc[-1] < 30


def test_bollinger_bands_ordering():
    s = pd.Series(np.random.RandomState(0).randn(100).cumsum() + 100)
    lower, mid, upper = bollinger(s, 20, 2.0)
    valid = mid.dropna().index
    assert (lower.loc[valid] <= mid.loc[valid]).all()
    assert (mid.loc[valid] <= upper.loc[valid]).all()


def test_atr_positive():
    rng = np.random.RandomState(1)
    close = pd.Series(rng.randn(100).cumsum() + 100)
    high = close + rng.rand(100)
    low = close - rng.rand(100)
    out = atr(high, low, close, 14)
    assert (out.dropna() > 0).all()
