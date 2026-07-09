"""Makine öğrenmesi katmanı — havuzlanmış gradient boosting, sızıntısız walk-forward.

Yöntem, modern varlık-fiyatlama ML literatürünü izler:
- **Gu, Kelly & Xiu (2020)** "Empirical Asset Pricing via Machine Learning" (RFS):
  tek küresel model, tüm sembollerin gözlemleri havuzlanır; ağaç toplulukları
  doğrusal olmayan etkileşimleri yakalar.
- **López de Prado (2018)** *Advances in Financial Machine Learning*: etiket ufku
  kadar **arındırma (purging)** — eğitim kümesinin sonu ile test yılının başı
  arasında etiketin geleceğe taştığı gözlemler atılır; aksi hâlde model geleceği
  "görmüş" olur.

Sızıntı korumaları:
1. Tüm öznitelikler t günü kapanışıyla hesaplanır (yalnız geçmişe bakan pencereler).
2. Etiket, t+1..t+ufuk getirisidir; eğitimde test yılına ``2×ufuk`` günden yakın
   gözlem kullanılmaz (arındırma tamponu).
3. Üretilen pozisyon, motorda +1 gün gecikmeyle uygulanır (``sinama.backtest``).
4. Hiperparametreler SABİTTİR (ayar taraması yok) ve RANDOM_STATE=42 —
   hiperparametre araması yapılsaydı bu da çoklu-test sayacına girerdi.
"""

from __future__ import annotations

import warnings

import numpy as np
import pandas as pd

RANDOM_STATE = 42
UFUK = 10          # etiket: gelecek 10 günün getirisi
ESIK = 0.55        # P(yükseliş) bu eşiği aşarsa uzun pozisyon
YILLIK_GUN = 365


def oznitelikler(kapanis: pd.Series) -> pd.DataFrame:
    """t günü kapanışında bilinen, ölçekten bağımsız öznitelik matrisi."""
    k = kapanis.astype(float)
    getiri = k.pct_change()
    df = pd.DataFrame(index=k.index)
    for n in (5, 10, 21, 63, 126, 252):
        df[f"mom_{n}"] = k.pct_change(n)
    df["vol_21"] = getiri.rolling(21).std() * np.sqrt(YILLIK_GUN)
    df["vol_63"] = getiri.rolling(63).std() * np.sqrt(YILLIK_GUN)
    df["vol_oran"] = df["vol_21"] / df["vol_63"]
    fark = k.diff()
    kazanc = fark.clip(lower=0).ewm(alpha=1 / 14, adjust=False).mean()
    kayip = (-fark.clip(upper=0)).ewm(alpha=1 / 14, adjust=False).mean()
    df["rsi_14"] = 100 - 100 / (1 + kazanc / kayip.replace(0, np.nan))
    macd = k.ewm(span=12, adjust=False).mean() - k.ewm(span=26, adjust=False).mean()
    df["macd_norm"] = (macd - macd.ewm(span=9, adjust=False).mean()) / k
    df["sma50_uzaklik"] = k / k.rolling(50).mean() - 1
    df["sma200_uzaklik"] = k / k.rolling(200).mean() - 1
    for n in (20, 55):
        alt = k.rolling(n).min()
        ust = k.rolling(n).max()
        df[f"kanal_{n}"] = (k - alt) / (ust - alt).replace(0, np.nan)
    df["dusus_durumu"] = k / k.cummax() - 1
    return df


def _havuz(seriler: dict[str, pd.Series]) -> pd.DataFrame:
    """Sembol×gün havuzlanmış öznitelik + etiket tablosu (Gu-Kelly-Xiu kurgusu)."""
    parcalar = []
    for sembol, kapanis in seriler.items():
        x = oznitelikler(kapanis)
        x["etiket"] = (kapanis.shift(-UFUK) / kapanis - 1 > 0).astype(float)
        x.loc[kapanis.shift(-UFUK).isna(), "etiket"] = np.nan  # ufku dolmayanlar
        x["sembol"] = sembol
        parcalar.append(x.reset_index(names="tarih"))
    return pd.concat(parcalar, ignore_index=True)


def ml_pozisyonlar(seriler: dict[str, pd.Series], esik: float = ESIK,
                   ufuk: int = UFUK, gunluk=print) -> dict[str, pd.Series]:
    """Yıllık yeniden eğitimli walk-forward ML pozisyonları (sembol → 0/1 serisi).

    Y yılının tahminleri, yalnız Y'den (arındırma tamponu kadar) önce biten
    verilerle eğitilmiş modelden gelir.
    """
    from sklearn.ensemble import HistGradientBoostingClassifier

    havuz = _havuz(seriler)
    ozn_kolonlari = [c for c in havuz.columns if c not in ("tarih", "sembol", "etiket")]
    ilk_yil = min(s.index[0].year for s in seriler.values()) + 3
    son_yil = max(s.index[-1].year for s in seriler.values())

    tahminler = []
    for yil in range(ilk_yil, son_yil + 1):
        sinir = pd.Timestamp(f"{yil}-01-01") - pd.Timedelta(days=2 * ufuk)  # arındırma
        egitim = havuz[(havuz.tarih < sinir) & havuz.etiket.notna()].dropna(
            subset=ozn_kolonlari)
        test = havuz[havuz.tarih.dt.year == yil].dropna(subset=ozn_kolonlari)
        if len(egitim) < 2000 or test.empty:
            continue
        model = HistGradientBoostingClassifier(
            max_iter=300, learning_rate=0.05, l2_regularization=1.0,
            early_stopping=False, random_state=RANDOM_STATE)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            model.fit(egitim[ozn_kolonlari], egitim["etiket"])
            p = model.predict_proba(test[ozn_kolonlari])[:, 1]
        tahminler.append(pd.DataFrame(
            {"tarih": test.tarih.values, "sembol": test.sembol.values, "p": p}))
        gunluk(f"ML {yil}: eğitim {len(egitim):,} gözlem → test {len(test):,} gözlem")

    tum = pd.concat(tahminler, ignore_index=True)
    pozisyonlar = {}
    for sembol, kapanis in seriler.items():
        t = tum[tum.sembol == sembol].set_index("tarih")["p"].sort_index()
        pozisyonlar[sembol] = (t.reindex(kapanis.index) > esik).astype(float)
    return pozisyonlar
