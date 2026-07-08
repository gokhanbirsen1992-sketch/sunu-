"""Literatür kaynaklı aday göstergeler.

Her fonksiyon, günlük kapanış serisinden **t günü kapanışında bilinen** bir hedef
pozisyon serisi üretir: 1 = uzun (long), 0 = nakit (flat). Pozisyonun getiriye
uygulanması bir gün gecikmeli yapılır (bkz. ``sinama.backtest`` içindeki
``shift(1)``) — ileri-bakış yanlılığı yapısal olarak engellenir.

Kaynaklar için bkz. ``alsat/LITERATUR.md``.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

YILLIK_GUN = 365  # kripto her gün işlem görür


def sma_kesisim(kapanis: pd.Series, kisa: int, uzun: int) -> pd.Series:
    """Kısa SMA > uzun SMA iken uzun pozisyon (Brock-Lakonishok-LeBaron 1992)."""
    k = kapanis.rolling(kisa).mean()
    u = kapanis.rolling(uzun).mean()
    return (k > u).astype(float)


def ema_kesisim(kapanis: pd.Series, kisa: int, uzun: int) -> pd.Series:
    """Kısa EMA > uzun EMA iken uzun pozisyon (BLL 1992'nin üstel çeşidi)."""
    k = kapanis.ewm(span=kisa, adjust=False).mean()
    u = kapanis.ewm(span=uzun, adjust=False).mean()
    return (k > u).astype(float)


def fiyat_sma(kapanis: pd.Series, pencere: int) -> pd.Series:
    """Fiyat SMA'nın üzerindeyken uzun pozisyon (Detzel ve ark. 2021: fiyat/MA oranı)."""
    return (kapanis > kapanis.rolling(pencere).mean()).astype(float)


def tsmom(kapanis: pd.Series, pencere: int) -> pd.Series:
    """Geçmiş ``pencere`` günlük getiri pozitifse uzun (Moskowitz-Ooi-Pedersen 2012)."""
    return (kapanis.pct_change(pencere) > 0).astype(float)


def donchian_kirilim(kapanis: pd.Series, giris: int, cikis: int) -> pd.Series:
    """Kanal kırılımı: önceki ``giris`` gün zirvesini aşınca gir, ``cikis`` gün
    dibinin altına inince çık (BLL 1992 "trading range break"; Donchian kanalı,
    kapanış tabanlı çeşit)."""
    ust = kapanis.shift(1).rolling(giris).max()
    alt = kapanis.shift(1).rolling(cikis).min()
    ham = pd.Series(np.nan, index=kapanis.index)
    ham[kapanis > ust] = 1.0
    ham[kapanis < alt] = 0.0
    return ham.ffill().fillna(0.0)


def rsi_esik(kapanis: pd.Series, pencere: int = 14, esik: float = 50.0) -> pd.Series:
    """Wilder (1978) RSI'ı eşiğin üstündeyken uzun pozisyon (momentum yorumu)."""
    fark = kapanis.diff()
    kazanc = fark.clip(lower=0).ewm(alpha=1 / pencere, adjust=False).mean()
    kayip = (-fark.clip(upper=0)).ewm(alpha=1 / pencere, adjust=False).mean()
    rs = kazanc / kayip.replace(0, np.nan)
    rsi = 100 - 100 / (1 + rs)
    return (rsi > esik).astype(float)


def macd_kural(kapanis: pd.Series, hizli: int = 12, yavas: int = 26,
               sinyal: int = 9) -> pd.Series:
    """MACD çizgisi sinyal çizgisinin üstündeyken uzun (Appel'in MACD'si)."""
    macd = (kapanis.ewm(span=hizli, adjust=False).mean()
            - kapanis.ewm(span=yavas, adjust=False).mean())
    return (macd > macd.ewm(span=sinyal, adjust=False).mean()).astype(float)


def bollinger_kirilim(kapanis: pd.Series, pencere: int = 20, k: float = 2.0) -> pd.Series:
    """Üst banda kırılımda gir, orta bandın altında çık (Bollinger; momentum çeşidi)."""
    orta = kapanis.rolling(pencere).mean()
    std = kapanis.rolling(pencere).std()
    ham = pd.Series(np.nan, index=kapanis.index)
    ham[kapanis > orta + k * std] = 1.0
    ham[kapanis < orta] = 0.0
    return ham.ffill().fillna(0.0)


def vol_hedef(pozisyon: pd.Series, kapanis: pd.Series, hedef_vol: float = 0.40,
              pencere: int = 30) -> pd.Series:
    """Pozisyonu gerçekleşen volatiliteye göre ölçekler (Moreira-Muir 2017;
    kripto momentum çöküşlerine karşı, bkz. LITERATUR §3). Kaldıraç yok: tavan 1."""
    gunluk = kapanis.pct_change()
    vol = gunluk.rolling(pencere).std() * np.sqrt(YILLIK_GUN)
    olcek = (hedef_vol / vol).clip(upper=1.0)
    return (pozisyon * olcek).fillna(0.0)


def topluluk(pozisyonlar: list[pd.Series], esik: float = 0.5) -> pd.Series:
    """Kural sınıflarının oy ortalaması eşiği aşarsa uzun (Hudson-Urquhart 2021:
    tek kural kırılgan, sınıflar birlikte daha sağlam)."""
    oy = pd.concat(pozisyonlar, axis=1).mean(axis=1)
    return (oy >= esik).astype(float)


# ── Aday havuzu tanımı ─────────────────────────────────────────────────────────
# Döngü motoru bu aileleri parametre ızgaralarıyla çarpar. Her aile literatüre bağlı.

AILELER: dict[str, dict] = {
    "sma_kesisim": {
        "fonk": sma_kesisim,
        "izgara": [{"kisa": k, "uzun": u} for k, u in
                   ((5, 20), (10, 50), (20, 100), (50, 200))],
        "kaynak": "Brock-Lakonishok-LeBaron 1992",
    },
    "ema_kesisim": {
        "fonk": ema_kesisim,
        "izgara": [{"kisa": k, "uzun": u} for k, u in ((10, 30), (20, 60))],
        "kaynak": "BLL 1992 (üstel çeşit)",
    },
    "fiyat_sma": {
        "fonk": fiyat_sma,
        "izgara": [{"pencere": p} for p in (5, 10, 20, 50, 100)],
        "kaynak": "Detzel ve ark. 2021",
    },
    "tsmom": {
        "fonk": tsmom,
        "izgara": [{"pencere": p} for p in (7, 14, 30, 60, 90)],
        "kaynak": "Moskowitz-Ooi-Pedersen 2012; Liu-Tsyvinski 2021",
    },
    "donchian_kirilim": {
        "fonk": donchian_kirilim,
        "izgara": [{"giris": g, "cikis": c} for g, c in
                   ((20, 10), (55, 20), (100, 50))],
        "kaynak": "BLL 1992 (trading range break); Donchian",
    },
    "rsi_esik": {
        "fonk": rsi_esik,
        "izgara": [{"pencere": 14, "esik": e} for e in (45.0, 50.0, 55.0)],
        "kaynak": "Wilder 1978",
    },
    "macd_kural": {
        "fonk": macd_kural,
        "izgara": [{"hizli": 12, "yavas": 26, "sinyal": 9}],
        "kaynak": "Appel (MACD)",
    },
    "bollinger_kirilim": {
        "fonk": bollinger_kirilim,
        "izgara": [{"pencere": 20, "k": 2.0}],
        "kaynak": "Bollinger 1992",
    },
}


def pozisyon_uret(kapanis: pd.Series, aile: str, parametreler: dict,
                  vol_filtre: float | None = None) -> pd.Series:
    """Aile adı + parametrelerden pozisyon serisi üretir; istenirse vol hedefi uygular."""
    poz = AILELER[aile]["fonk"](kapanis, **parametreler)
    if vol_filtre is not None:
        poz = vol_hedef(poz, kapanis, hedef_vol=vol_filtre)
    return poz
