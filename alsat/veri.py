"""Veri katmanı — anahtarsız kaynaklardan günlük kapanış serisi.

Kaynak zinciri (ilk başarılı olan kullanılır):
1. Binance ``/api/v3/klines`` (tam OHLCV, 2017'den bugüne, 1000'lik sayfalama)
2. Crypto.com Exchange ``public/get-candlestick``
3. Coin Metrics topluluk verisi (GitHub, yalnız günlük kapanış ``PriceUSD``,
   2010'dan bugüne) — kısıtlı ağlarda çoğu zaman tek erişilebilir kaynak.

Göstergelerin tamamı kapanış fiyatından hesaplandığı için modülün ortak veri
sözleşmesi tek sütundur: ``tarih`` indeksli ``kapanis`` serisi. CSV yükleyici
herhangi bir piyasadan (BIST, ABD, kripto) günlük seriyle çalışmayı sağlar.
"""

from __future__ import annotations

import io
import time
from pathlib import Path

import httpx
import numpy as np
import pandas as pd

ZAMAN_ASIMI = httpx.Timeout(30.0)

BINANCE_URL = "https://api.binance.com/api/v3/klines"
CRYPTOCOM_URL = "https://api.crypto.com/exchange/v1/public/get-candlestick"
COINMETRICS_URL = "https://raw.githubusercontent.com/coinmetrics/data/master/csv/{varlik}.csv"

# BTCUSDT → btc gibi eşlemeler (Coin Metrics varlık kodları)
_COINMETRICS_ESLEME = {
    "BTCUSDT": "btc", "ETHUSDT": "eth", "BNBUSDT": "bnb", "ADAUSDT": "ada",
    "XRPUSDT": "xrp", "SOLUSDT": "sol", "LTCUSDT": "ltc", "DOGEUSDT": "doge",
}

_KAPANIS_ADAYLARI = ("kapanis", "close", "priceusd", "adj close", "adj_close", "price", "kapanış")
_TARIH_ADAYLARI = ("tarih", "time", "date", "timestamp", "datetime")


def _seri_yap(tarih, kapanis) -> pd.Series:
    tarih_idx = pd.Index(tarih)
    if pd.api.types.is_numeric_dtype(tarih_idx):  # Binance/Crypto.com: ms epoch
        zaman = pd.to_datetime(tarih_idx, unit="ms", utc=True, errors="coerce")
    else:
        zaman = pd.to_datetime(tarih_idx, utc=True, errors="coerce", format="mixed")
    deger = pd.to_numeric(pd.Index(kapanis), errors="coerce")
    seri = pd.Series(
        np.asarray(deger, dtype=float),
        index=pd.DatetimeIndex(zaman).tz_localize(None),
        name="kapanis",
    )
    seri = seri[~seri.index.isna()].dropna()
    seri = seri[~seri.index.duplicated(keep="last")].sort_index()
    if len(seri) < 200:
        raise ValueError(f"Yetersiz veri: {len(seri)} gün (< 200)")
    return seri


def binance_gunluk(sembol: str, istemci: httpx.Client | None = None) -> pd.Series:
    """Binance'ten tüm günlük kapanışları çeker (anahtarsız, 1000'lik sayfalama)."""
    kapat = istemci is None
    istemci = istemci or httpx.Client(timeout=ZAMAN_ASIMI)
    try:
        satirlar: list[list] = []
        baslangic = 0
        while True:
            yanit = istemci.get(BINANCE_URL, params={
                "symbol": sembol, "interval": "1d", "limit": 1000, "startTime": baslangic,
            })
            yanit.raise_for_status()
            parca = yanit.json()
            if not parca:
                break
            satirlar.extend(parca)
            if len(parca) < 1000:
                break
            baslangic = parca[-1][6] + 1  # son mumun kapanış zamanı + 1 ms
            time.sleep(0.2)
        return _seri_yap([s[0] for s in satirlar], [s[4] for s in satirlar])
    finally:
        if kapat:
            istemci.close()


def cryptocom_gunluk(sembol: str, istemci: httpx.Client | None = None) -> pd.Series:
    """Crypto.com Exchange public REST'ten günlük kapanışlar (BTCUSDT → BTC_USDT)."""
    enstruman = sembol.replace("USDT", "_USDT") if "_" not in sembol else sembol
    kapat = istemci is None
    istemci = istemci or httpx.Client(timeout=ZAMAN_ASIMI)
    try:
        mumlar: list[dict] = []
        bitis: int | None = None
        for _ in range(40):  # 40 × 300 mum ≈ 32 yıl tavanı
            params = {"instrument_name": enstruman, "timeframe": "1D", "count": 300}
            if bitis is not None:
                params["end_ts"] = bitis
            yanit = istemci.get(CRYPTOCOM_URL, params=params)
            yanit.raise_for_status()
            parca = (yanit.json().get("result") or {}).get("data") or []
            if not parca:
                break
            mumlar = parca + mumlar
            en_eski = min(int(m["t"]) for m in parca)
            if bitis is not None and en_eski >= bitis:
                break
            bitis = en_eski - 1
            if len(parca) < 300:
                break
            time.sleep(0.2)
        return _seri_yap([int(m["t"]) for m in mumlar], [m["c"] for m in mumlar])
    finally:
        if kapat:
            istemci.close()


def coinmetrics_gunluk(sembol: str, istemci: httpx.Client | None = None) -> pd.Series:
    """Coin Metrics topluluk CSV'sinden günlük ``PriceUSD`` serisi (GitHub üzerinden)."""
    varlik = _COINMETRICS_ESLEME.get(sembol.upper())
    if varlik is None:
        raise ValueError(f"Coin Metrics eşlemesi yok: {sembol}")
    kapat = istemci is None
    istemci = istemci or httpx.Client(timeout=ZAMAN_ASIMI, follow_redirects=True)
    try:
        yanit = istemci.get(COINMETRICS_URL.format(varlik=varlik))
        yanit.raise_for_status()
        df = pd.read_csv(io.StringIO(yanit.text), usecols=["time", "PriceUSD"])
        df = df.dropna()
        return _seri_yap(df["time"], df["PriceUSD"])
    finally:
        if kapat:
            istemci.close()


def csv_yukle(yol: str | Path) -> pd.Series:
    """Herhangi bir günlük OHLCV/kapanış CSV'sini ortak sözleşmeye çevirir."""
    df = pd.read_csv(yol)
    kolonlar = {k.strip().lower(): k for k in df.columns}
    tarih_k = next((kolonlar[a] for a in _TARIH_ADAYLARI if a in kolonlar), None)
    kapanis_k = next((kolonlar[a] for a in _KAPANIS_ADAYLARI if a in kolonlar), None)
    if tarih_k is None or kapanis_k is None:
        raise ValueError(
            f"CSV'de tarih/kapanış sütunu bulunamadı; mevcut sütunlar: {list(df.columns)}"
        )
    return _seri_yap(df[tarih_k], df[kapanis_k])


def veri_getir(sembol: str, veri_dizini: str | Path = "data/alsat_cache",
               yenile: bool = False) -> tuple[pd.Series, str]:
    """Önbellekten ya da kaynak zincirinden günlük kapanış serisi döndürür.

    Dönüş: (seri, kaynak_adi). Önbellek dosyası: ``<dizin>/<sembol>_1d.csv``.
    """
    dizin = Path(veri_dizini)
    dizin.mkdir(parents=True, exist_ok=True)
    onbellek = dizin / f"{sembol.upper()}_1d.csv"
    if onbellek.exists() and not yenile:
        return csv_yukle(onbellek), f"önbellek ({onbellek})"

    hatalar: list[str] = []
    for ad, fonk in (("Binance", binance_gunluk),
                     ("Crypto.com", cryptocom_gunluk),
                     ("Coin Metrics (GitHub)", coinmetrics_gunluk)):
        try:
            seri = fonk(sembol)
            seri.rename_axis("tarih").reset_index().to_csv(onbellek, index=False)
            return seri, ad
        except Exception as h:  # kaynak düşse bile zincir devam eder
            hatalar.append(f"{ad}: {type(h).__name__}: {h}")
    raise RuntimeError("Hiçbir veri kaynağına ulaşılamadı:\n" + "\n".join(hatalar))
