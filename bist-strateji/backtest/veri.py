"""Veri katmanı.

1) `sentetik_bist(...)`: BIST karakterine (XU100 / BIST hisseleri) kalibre edilmiş
   rejim-değişimli sentetik OHLCV üretir. Amaç strateji turnuvasını yüzlerce
   farklı ama gerçekçi senaryoda koşturmaktır — bu bir tahmin değil, sağlamlık
   (robustness) test alanıdır.

   Kalibrasyon hedefleri (TL bazlı, yaklaşık):
   - Uzun vadeli nominal sürüklenme yüksek (enflasyonist ortam): yıllık ~%30-45
   - Yıllık oynaklık: endeks ~%30, hisse ~%45
   - 1.5-3 yılda bir, -%25 ile -%45 arası ayı fazı; ara ara sert tek gün düşüşleri
   - Uzun yatay/testere dönemleri (trend stratejilerini cezalandırır)

2) `csv_yukle(path)`: Gerçek veri için TradingView dışa aktarımı veya
   time/open/high/low/close(/volume) kolonlu herhangi bir CSV'yi okur.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

REJIMLER = {
    # ad: (günlük ort. log-getiri, günlük vol, ort. süre gün)
    "boga": (0.0026, 0.013, 140),
    "yatay": (0.0004, 0.010, 80),
    "ayi": (-0.0030, 0.022, 35),
}
GECIS = {
    "boga": [("boga", 0.0), ("yatay", 0.75), ("ayi", 0.25)],
    "yatay": [("boga", 0.65), ("yatay", 0.0), ("ayi", 0.35)],
    "ayi": [("boga", 0.45), ("yatay", 0.55), ("ayi", 0.0)],
}


def sentetik_bist(
    n_gun: int = 2520,
    seed: int = 0,
    hisse_mi: bool = False,
    baslangic: float = 1000.0,
) -> pd.DataFrame:
    """~n_gun işlem günü OHLCV üretir (10 yıl ≈ 2520 gün)."""
    rng = np.random.default_rng(seed)
    vol_carpan = 1.5 if hisse_mi else 1.0
    drift_carpan = 1.1 if hisse_mi else 1.0

    rejim = rng.choice(["boga", "yatay", "ayi"], p=[0.5, 0.35, 0.15])
    kalan = int(rng.exponential(REJIMLER[rejim][2])) + 5
    duzeltme_kalan = 0  # boğa/yatay içi sert düzeltme fazı (BIST'e özgü şok günleri)
    log_r = np.zeros(n_gun)
    for i in range(n_gun):
        mu, sig, _ = REJIMLER[rejim]
        mu *= drift_carpan
        sig *= vol_carpan
        if duzeltme_kalan > 0:
            # Politik/kur şoku tarzı kısa-sert düzeltme (ör. Mar/Kas 2021, Tem 2023)
            mu, sig = -0.013, 0.030 * vol_carpan
            duzeltme_kalan -= 1
        elif rejim != "ayi" and rng.random() < 0.0035:
            duzeltme_kalan = int(rng.integers(4, 11))
        r = rng.normal(mu, sig)
        # Nadir sıçrama günleri (BIST devre kesici tarzı sert hareketler)
        if rng.random() < 0.003:
            r += rng.choice([-1, 1], p=[0.6, 0.4]) * rng.uniform(0.04, 0.08)
        log_r[i] = r
        kalan -= 1
        if kalan <= 0:
            adlar, agirliklar = zip(*[(a, p) for a, p in GECIS[rejim] if p > 0])
            rejim = rng.choice(adlar, p=np.array(agirliklar) / sum(agirliklar))
            kalan = int(rng.exponential(REJIMLER[rejim][2])) + 5

    close = baslangic * np.exp(np.cumsum(log_r))
    prev_close = np.roll(close, 1)
    prev_close[0] = baslangic
    gap = rng.normal(0, 0.003 * vol_carpan, n_gun)
    open_ = prev_close * np.exp(gap)
    gunici = np.abs(rng.normal(0, 0.008 * vol_carpan, n_gun)) + 0.002
    high = np.maximum(open_, close) * (1 + gunici)
    low = np.minimum(open_, close) * (1 - gunici)
    volume = rng.lognormal(mean=13, sigma=0.6, size=n_gun) * (1 + 3 * gunici)

    idx = pd.bdate_range("2016-01-04", periods=n_gun)
    return pd.DataFrame(
        {"open": open_, "high": high, "low": low, "close": close, "volume": volume}, index=idx
    )


def haftalik(df: pd.DataFrame) -> pd.DataFrame:
    """Günlük OHLCV'den haftalık bar üretir (TradingView haftalık ile aynı mantık)."""
    o = df["open"].resample("W-FRI").first()
    h = df["high"].resample("W-FRI").max()
    l = df["low"].resample("W-FRI").min()
    c = df["close"].resample("W-FRI").last()
    v = df["volume"].resample("W-FRI").sum()
    out = pd.DataFrame({"open": o, "high": h, "low": l, "close": c, "volume": v}).dropna()
    return out


def csv_yukle(path: str) -> pd.DataFrame:
    """TradingView dışa aktarımı veya genel OHLC CSV okur.

    Beklenen kolonlar (büyük/küçük harf duyarsız): time/date/tarih,
    open/açılış, high/yüksek, low/düşük, close/kapanış, volume/hacim(ops.).
    """
    df = pd.read_csv(path)
    df.columns = [c.strip().lower() for c in df.columns]
    esle = {
        "time": "time", "date": "time", "tarih": "time", "datetime": "time",
        "open": "open", "açılış": "open", "acilis": "open",
        "high": "high", "yüksek": "high", "yuksek": "high",
        "low": "low", "düşük": "low", "dusuk": "low",
        "close": "close", "kapanış": "close", "kapanis": "close", "price": "close",
        "volume": "volume", "hacim": "volume", "vol": "volume",
    }
    df = df.rename(columns={c: esle[c] for c in df.columns if c in esle})
    if "time" not in df.columns:
        raise ValueError("CSV'de time/date/tarih kolonu bulunamadı")
    # TradingView unix saniye veya ISO tarih verebilir
    if np.issubdtype(df["time"].dtype, np.number):
        df["time"] = pd.to_datetime(df["time"], unit="s")
    else:
        df["time"] = pd.to_datetime(df["time"])
    df = df.set_index("time").sort_index()
    for k in ("open", "high", "low"):
        if k not in df.columns:
            df[k] = df["close"]
    if "volume" not in df.columns:
        df["volume"] = 0.0
    return df[["open", "high", "low", "close", "volume"]].astype(float).dropna()
