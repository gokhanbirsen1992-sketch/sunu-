"""Teknik indikatör kütüphanesi — TradingView (Pine v6) ile birebir uyumlu hesaplama.

Tüm fonksiyonlar numpy dizileri alır/döndürür. Wilder tabanlı indikatörler
(RSI, ATR, ADX) Pine'daki gibi RMA (Wilder yumuşatması) kullanır.
"""
from __future__ import annotations

import numpy as np


def sma(x: np.ndarray, n: int) -> np.ndarray:
    out = np.full_like(x, np.nan, dtype=float)
    if n <= 0 or len(x) < n:
        return out
    c = np.cumsum(np.insert(x.astype(float), 0, 0.0))
    out[n - 1:] = (c[n:] - c[:-n]) / n
    return out


def ema(x: np.ndarray, n: int) -> np.ndarray:
    out = np.full_like(x, np.nan, dtype=float)
    if n <= 0 or len(x) < n:
        return out
    alpha = 2.0 / (n + 1.0)
    out[n - 1] = np.mean(x[:n])
    for i in range(n, len(x)):
        out[i] = alpha * x[i] + (1 - alpha) * out[i - 1]
    return out


def rma(x: np.ndarray, n: int) -> np.ndarray:
    """Wilder yumuşatması (Pine: ta.rma). İlk değer n-bar SMA."""
    out = np.full_like(x, np.nan, dtype=float)
    if n <= 0 or len(x) < n:
        return out
    alpha = 1.0 / n
    out[n - 1] = np.nanmean(x[:n])
    for i in range(n, len(x)):
        out[i] = alpha * x[i] + (1 - alpha) * out[i - 1]
    return out


def wma(x: np.ndarray, n: int) -> np.ndarray:
    out = np.full_like(x, np.nan, dtype=float)
    if n <= 0 or len(x) < n:
        return out
    w = np.arange(1, n + 1, dtype=float)
    ws = w.sum()
    for i in range(n - 1, len(x)):
        out[i] = np.dot(x[i - n + 1: i + 1], w) / ws
    return out


def hma(x: np.ndarray, n: int) -> np.ndarray:
    """Hull Moving Average (Alan Hull, 2005)."""
    half = max(1, n // 2)
    sq = max(1, int(round(np.sqrt(n))))
    raw = 2 * wma(x, half) - wma(x, n)
    return wma(raw, sq)


def roc(x: np.ndarray, n: int) -> np.ndarray:
    out = np.full_like(x, np.nan, dtype=float)
    out[n:] = (x[n:] / x[:-n] - 1.0) * 100.0
    return out


def rsi(close: np.ndarray, n: int = 14) -> np.ndarray:
    """RSI (Wilder, 1978) — Pine ta.rsi ile uyumlu (RMA tabanlı)."""
    d = np.diff(close, prepend=close[0])
    up = np.where(d > 0, d, 0.0)
    dn = np.where(d < 0, -d, 0.0)
    up[0] = np.nan
    dn[0] = np.nan
    # Pine, ilk barın değişimini dışlayıp kalan seride RMA başlatır.
    avg_up = _rma_skip_nan(up, n)
    avg_dn = _rma_skip_nan(dn, n)
    out = np.full_like(close, np.nan, dtype=float)
    with np.errstate(divide="ignore", invalid="ignore"):
        rs = avg_up / avg_dn
        out = np.where(avg_dn == 0, 100.0, np.where(avg_up == 0, 0.0, 100.0 - 100.0 / (1.0 + rs)))
    out[np.isnan(avg_up) | np.isnan(avg_dn)] = np.nan
    return out


def _rma_skip_nan(x: np.ndarray, n: int) -> np.ndarray:
    out = np.full_like(x, np.nan, dtype=float)
    start = np.argmax(~np.isnan(x))
    if np.isnan(x[start]):
        return out
    seg = x[start:]
    if len(seg) < n:
        return out
    r = rma(seg, n)
    out[start:] = r
    return out


def true_range(high: np.ndarray, low: np.ndarray, close: np.ndarray) -> np.ndarray:
    prev_c = np.roll(close, 1)
    tr = np.maximum(high - low, np.maximum(np.abs(high - prev_c), np.abs(low - prev_c)))
    tr[0] = high[0] - low[0]
    return tr


def atr(high: np.ndarray, low: np.ndarray, close: np.ndarray, n: int = 14) -> np.ndarray:
    return rma(true_range(high, low, close), n)


def adx(high: np.ndarray, low: np.ndarray, close: np.ndarray, n: int = 14) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Wilder ADX. Döndürür: (adx, +DI, -DI)."""
    up = np.diff(high, prepend=high[0])
    dn = -np.diff(low, prepend=low[0])
    plus_dm = np.where((up > dn) & (up > 0), up, 0.0)
    minus_dm = np.where((dn > up) & (dn > 0), dn, 0.0)
    tr = true_range(high, low, close)
    atr_ = rma(tr, n)
    with np.errstate(divide="ignore", invalid="ignore"):
        plus_di = 100.0 * rma(plus_dm, n) / atr_
        minus_di = 100.0 * rma(minus_dm, n) / atr_
        dx = 100.0 * np.abs(plus_di - minus_di) / (plus_di + minus_di)
    dx[~np.isfinite(dx)] = np.nan
    adx_ = _rma_skip_nan(dx, n)
    return adx_, plus_di, minus_di


def macd(close: np.ndarray, fast: int = 12, slow: int = 26, signal: int = 9) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """MACD (Gerald Appel). Döndürür: (macd, sinyal, histogram)."""
    line = ema(close, fast) - ema(close, slow)
    sig = _ema_skip_nan(line, signal)
    return line, sig, line - sig


def _ema_skip_nan(x: np.ndarray, n: int) -> np.ndarray:
    out = np.full_like(x, np.nan, dtype=float)
    valid = ~np.isnan(x)
    if not valid.any():
        return out
    start = np.argmax(valid)
    seg = x[start:]
    if len(seg) < n:
        return out
    out[start:] = ema(seg, n)
    return out


def bollinger(close: np.ndarray, n: int = 20, k: float = 2.0) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    mid = sma(close, n)
    sd = np.full_like(close, np.nan, dtype=float)
    for i in range(n - 1, len(close)):
        sd[i] = np.std(close[i - n + 1: i + 1])
    return mid, mid + k * sd, mid - k * sd


def donchian(high: np.ndarray, low: np.ndarray, n: int = 20) -> tuple[np.ndarray, np.ndarray]:
    """Donchian kanalı (Richard Donchian / Turtle). Döndürür: (üst, alt) — geçmiş n bar."""
    hh = np.full_like(high, np.nan, dtype=float)
    ll = np.full_like(low, np.nan, dtype=float)
    for i in range(n - 1, len(high)):
        hh[i] = np.max(high[i - n + 1: i + 1])
        ll[i] = np.min(low[i - n + 1: i + 1])
    return hh, ll


def supertrend(high: np.ndarray, low: np.ndarray, close: np.ndarray, n: int = 10, mult: float = 3.0) -> tuple[np.ndarray, np.ndarray]:
    """Supertrend (Olivier Seban). Döndürür: (çizgi, yön) — yön: +1 yukarı, -1 aşağı.

    Pine ta.supertrend ile aynı kural seti (ATR = RMA).
    """
    hl2 = (high + low) / 2.0
    a = atr(high, low, close, n)
    upper = hl2 + mult * a
    lower = hl2 - mult * a
    st = np.full_like(close, np.nan, dtype=float)
    direction = np.zeros(len(close), dtype=int)
    fu = np.full_like(close, np.nan, dtype=float)
    fl = np.full_like(close, np.nan, dtype=float)
    started = False
    for i in range(len(close)):
        if np.isnan(a[i]):
            continue
        if not started:
            fu[i], fl[i] = upper[i], lower[i]
            direction[i] = -1 if close[i] <= fu[i] else 1
            st[i] = fu[i] if direction[i] == -1 else fl[i]
            started = True
            continue
        fu[i] = upper[i] if (upper[i] < fu[i - 1] or close[i - 1] > fu[i - 1]) else fu[i - 1]
        fl[i] = lower[i] if (lower[i] > fl[i - 1] or close[i - 1] < fl[i - 1]) else fl[i - 1]
        if direction[i - 1] == -1:
            direction[i] = 1 if close[i] > fu[i] else -1
        else:
            direction[i] = -1 if close[i] < fl[i] else 1
        st[i] = fl[i] if direction[i] == 1 else fu[i]
    return st, direction


def kama(close: np.ndarray, n: int = 10, fast: int = 2, slow: int = 30) -> np.ndarray:
    """Kaufman Adaptive MA (Perry Kaufman, 1998)."""
    out = np.full_like(close, np.nan, dtype=float)
    if len(close) <= n:
        return out
    fast_sc = 2.0 / (fast + 1.0)
    slow_sc = 2.0 / (slow + 1.0)
    out[n] = close[n]
    for i in range(n + 1, len(close)):
        change = abs(close[i] - close[i - n])
        vol = np.sum(np.abs(np.diff(close[i - n: i + 1])))
        er = change / vol if vol > 0 else 0.0
        sc = (er * (fast_sc - slow_sc) + slow_sc) ** 2
        out[i] = out[i - 1] + sc * (close[i] - out[i - 1])
    return out


def chandelier_exit_long(high: np.ndarray, low: np.ndarray, close: np.ndarray, n: int = 22, mult: float = 3.0) -> np.ndarray:
    """Chandelier Exit — uzun taraf (Chuck LeBeau): HH(n) - mult*ATR(n)."""
    hh, _ = donchian(high, low, n)
    return hh - mult * atr(high, low, close, n)


def stochastic(high: np.ndarray, low: np.ndarray, close: np.ndarray, k: int = 14, d: int = 3, smooth: int = 3) -> tuple[np.ndarray, np.ndarray]:
    hh, ll = donchian(high, low, k)
    with np.errstate(divide="ignore", invalid="ignore"):
        raw = 100.0 * (close - ll) / (hh - ll)
    raw[~np.isfinite(raw)] = np.nan
    k_line = _sma_skip_nan(raw, smooth)
    d_line = _sma_skip_nan(k_line, d)
    return k_line, d_line


def _sma_skip_nan(x: np.ndarray, n: int) -> np.ndarray:
    out = np.full_like(x, np.nan, dtype=float)
    valid = ~np.isnan(x)
    if not valid.any():
        return out
    start = np.argmax(valid)
    seg = x[start:]
    if len(seg) < n:
        return out
    out[start:] = sma(seg, n)
    return out


def obv(close: np.ndarray, volume: np.ndarray) -> np.ndarray:
    d = np.sign(np.diff(close, prepend=close[0]))
    d[0] = 0
    return np.cumsum(d * volume)


def cmf(high: np.ndarray, low: np.ndarray, close: np.ndarray, volume: np.ndarray, n: int = 20) -> np.ndarray:
    """Chaikin Money Flow."""
    with np.errstate(divide="ignore", invalid="ignore"):
        mfm = ((close - low) - (high - close)) / (high - low)
    mfm[~np.isfinite(mfm)] = 0.0
    mfv = mfm * volume
    num = sma(mfv, n) * n
    den = sma(volume, n) * n
    with np.errstate(divide="ignore", invalid="ignore"):
        out = num / den
    return out
