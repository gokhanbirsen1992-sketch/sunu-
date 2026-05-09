"""Crypto.com Exchange public REST client (yalnızca okuma)."""
from __future__ import annotations

import logging
import time
from typing import Any

import httpx
import pandas as pd

logger = logging.getLogger(__name__)

BASE_URL = "https://api.crypto.com/exchange/v1"
DEFAULT_TIMEOUT = 10.0
MAX_RETRIES = 3


class ExchangeError(RuntimeError):
    """Borsa API hatası."""


class Exchange:
    """Crypto.com Exchange public endpoint'leri için minimum istemci."""

    def __init__(self, base_url: str = BASE_URL, timeout: float = DEFAULT_TIMEOUT):
        self._client = httpx.Client(base_url=base_url, timeout=timeout)

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "Exchange":
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

    def _request(self, path: str, params: dict[str, Any]) -> dict[str, Any]:
        last_exc: Exception | None = None
        for attempt in range(MAX_RETRIES):
            try:
                resp = self._client.get(path, params=params)
                resp.raise_for_status()
                payload = resp.json()
                if payload.get("code", 0) != 0:
                    raise ExchangeError(
                        f"API kodu hatası: {payload.get('code')} {payload.get('message')}"
                    )
                return payload.get("result", {})
            except (httpx.HTTPError, ExchangeError) as exc:
                last_exc = exc
                wait = 2**attempt
                logger.warning(
                    "API isteği başarısız (deneme %d/%d): %s — %ss sonra tekrar",
                    attempt + 1,
                    MAX_RETRIES,
                    exc,
                    wait,
                )
                time.sleep(wait)
        raise ExchangeError(f"API isteği {MAX_RETRIES} denemede başarısız: {last_exc}")

    def get_candles(
        self, symbol: str = "BTC_USDT", timeframe: str = "1D", count: int = 300
    ) -> pd.DataFrame:
        """Tarihsel mum verisi. Eski → yeni sıralı DataFrame döner."""
        result = self._request(
            "/public/get-candlestick",
            {"instrument_name": symbol, "timeframe": timeframe, "count": count},
        )
        rows = result.get("data", [])
        if not rows:
            raise ExchangeError(f"Boş mum verisi: {symbol} {timeframe}")
        df = _normalize_candles(rows)
        return df.sort_values("timestamp").reset_index(drop=True)

    def get_ticker(self, symbol: str = "BTC_USDT") -> dict[str, float]:
        """Anlık fiyat. {'price': float, 'bid': float, 'ask': float} döner."""
        result = self._request(
            "/public/get-tickers", {"instrument_name": symbol}
        )
        rows = result.get("data", [])
        if not rows:
            raise ExchangeError(f"Boş ticker yanıtı: {symbol}")
        t = rows[0]
        # Crypto.com v1 ticker alanları: a=last, b=bid, k=ask
        last = t.get("a") or t.get("last") or t.get("close")
        bid = t.get("b") or t.get("bid")
        ask = t.get("k") or t.get("ask")
        return {
            "price": float(last),
            "bid": float(bid) if bid is not None else float(last),
            "ask": float(ask) if ask is not None else float(last),
        }


def _normalize_candles(rows: list[dict]) -> pd.DataFrame:
    """API yanıtını ortak şemaya dönüştür: timestamp, open, high, low, close, volume.

    Crypto.com v1 short-key formatı (t,o,h,l,c,v) ve uzun anahtar formatı
    (open/high/low/close/volume/timestamp) — her ikisini destekler.
    """
    sample = rows[0]
    if "t" in sample:  # short keys
        df = pd.DataFrame(rows)
        df["timestamp"] = pd.to_datetime(df["t"].astype("int64"), unit="ms", utc=True)
        df = df.rename(columns={"o": "open", "h": "high", "l": "low", "c": "close", "v": "volume"})
    else:  # long keys
        df = pd.DataFrame(rows)
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)

    for col in ("open", "high", "low", "close", "volume"):
        df[col] = df[col].astype(float)
    return df[["timestamp", "open", "high", "low", "close", "volume"]]
