# Modül 16 — Uçtan Uca Proje: Trading Verisiyle Gerçek Pipeline

> **Hedef:** Öğrendiğin her şeyi tek bir gerçekçi projede birleştirmek. Bu
> repodaki **BTC/USDT botunun** verisini kullanarak, betimsel analizden modern
> doğrulamalı modellemeye kadar tüm zinciri kuracaksın.

> ⚠️ Bu bir **eğitim alıştırmasıdır**, yatırım tavsiyesi değildir. Amaç
> *metodoloji* öğrenmek; finansal getirileri tahmin etmek gerçekten zordur ve
> çoğu model naive baseline'ı zar zor yener.

---

## 0. Proje hedefi

**Soru:** "Yarın BTC yükselecek mi?" (ikili sınıflandırma) — ve daha önemlisi:
**bunu istatistiksel olarak dürüst biçimde nasıl test ederiz?**

Akış: Veri → Keşif → Özellik → Model → Doğrulama → Yorum → Eleştiri.

---

## 1. Veriyi al (repodaki istemciyle)

```python
# Bu repodaki mevcut altyapıyı kullan
from src.exchange import Exchange   # Crypto.com public client

ex = Exchange()
mumlar = ex.get_candlesticks("BTC_USDT", timeframe="1D", count=1000)
import pandas as pd
df = pd.DataFrame(mumlar)   # open, high, low, close, volume, timestamp
df["close"] = df["close"].astype(float)
df = df.sort_values("timestamp").reset_index(drop=True)
```

---

## 2. Keşifçi analiz (Modül 01, 03)

```python
df["getiri"] = df["close"].pct_change()
print(df["getiri"].describe())
print("Çarpıklık:", df["getiri"].skew(), "Basıklık:", df["getiri"].kurtosis())
# Beklenti: sıfıra yakın ortalama, şişman kuyruk (yüksek kurtosis)
```

- Histogram + boxplot çiz. Getiri normal mi? (Hayır — QQ-plot ile doğrula, Modül 03.)
- Aykırı günleri (IQR kuralı) işaretle — kriz/pump günleri.

---

## 3. Özellik mühendisliği (Modül 05, 09)

Repodaki `src/indicators.py` zaten RSI, EMA, Bollinger, ATR içeriyor — kullan!

```python
from src import indicators as ind

df["rsi"]      = ind.rsi(df["close"], 14)
df["ema_fark"] = ind.ema(df["close"], 20) - ind.ema(df["close"], 50)
df["atr"]      = ind.atr(df, 14)
df["mom_5"]    = df["close"].pct_change(5)
df["vol_10"]   = df["getiri"].rolling(10).std()      # gerçekleşen oynaklık
df["hacim_z"]  = (df["volume"] - df["volume"].rolling(20).mean()) \
                 / df["volume"].rolling(20).std()

# HEDEF: yarın yükseldi mi? (1/0) — DİKKAT: shift(-1) sadece hedef için!
df["hedef"] = (df["close"].shift(-1) > df["close"]).astype(int)

df = df.dropna().reset_index(drop=True)
```

> ⚠️ **Sızıntı kontrolü (Modül 08):** Tüm özellikler **sadece geçmiş/şimdiki**
> bilgiyi kullanmalı. `hedef` dışında hiçbir yerde `shift(-1)` / geleceğe bakan
> rolling olmamalı. Bir kez daha gözden geçir — en sık kaybedilen yer burası.

---

## 4. Zaman-bilinçli bölme (Modül 08, 12)

```python
ozellikler = ["rsi", "ema_fark", "atr", "mom_5", "vol_10", "hacim_z"]
X, y = df[ozellikler], df["hedef"]

# ASLA shuffle etme! Kronolojik böl.
n = len(df); kes = int(n * 0.8)
X_tr, X_te = X.iloc[:kes], X.iloc[kes:]
y_tr, y_te = y.iloc[:kes], y.iloc[kes:]
```

---

## 5. Modelleme — basitten karmaşığa (Modül 04, 06, 07, 10)

### Baseline (her zaman önce!)
```python
# Naive: "yarın = bugünün yönü" yani çoğunluk sınıfı
from sklearn.dummy import DummyClassifier
from sklearn.metrics import roc_auc_score, accuracy_score
base = DummyClassifier(strategy="most_frequent").fit(X_tr, y_tr)
print("Baseline acc:", accuracy_score(y_te, base.predict(X_te)))
```

### Lojistik regresyon (yorumlanabilir taban — Modül 06, 07)
```python
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression

logit = Pipeline([("sc", StandardScaler()),
                  ("clf", LogisticRegression(C=1.0, max_iter=1000))]).fit(X_tr, y_tr)
print("Logit AUC:", roc_auc_score(y_te, logit.predict_proba(X_te)[:, 1]))
```

### Gradient Boosting (güç — Modül 10)
```python
import xgboost as xgb
# Zaman serisi için iç doğrulama: son %20'yi val yap
v = int(len(X_tr) * 0.8)
xgbm = xgb.XGBClassifier(n_estimators=600, learning_rate=0.03, max_depth=3,
                         subsample=0.8, colsample_bytree=0.8, reg_lambda=1.0,
                         eval_metric="auc", early_stopping_rounds=50, n_jobs=-1)
xgbm.fit(X_tr.iloc[:v], y_tr.iloc[:v],
         eval_set=[(X_tr.iloc[v:], y_tr.iloc[v:])], verbose=False)
print("XGB AUC:", roc_auc_score(y_te, xgbm.predict_proba(X_te)[:, 1]))
```

---

## 6. Dürüst doğrulama: Walk-forward (Modül 08, 12)

Tek bölme şanslı olabilir. Zaman serisi CV ile tekrarla:

```python
from sklearn.model_selection import TimeSeriesSplit, cross_val_score
import numpy as np
tscv = TimeSeriesSplit(n_splits=5)
auc = cross_val_score(logit, X, y, cv=tscv, scoring="roc_auc")
print(f"Walk-forward AUC: {auc.mean():.3f} ± {auc.std():.3f}")
```

> Eğer AUC ≈ 0.50, model şanstan iyi değil — bu **normal ve dürüst** bir sonuç.
> Finansal yön tahmini gerçekten zordur. 0.53-0.55 bile, maliyetler sonrası,
> anlamlı olabilir ama istatistiksel olarak (Modül 04) doğrulanmalı.

---

## 7. Açıklama (Modül 15)

```python
import shap
expl = shap.TreeExplainer(xgbm)
shap.summary_plot(expl.shap_values(X_te), X_te)
# Model en çok hangi göstergeye dayanıyor? Yönü mantıklı mı?
```

---

## 8. Belirsizlik (Modül 11 veya 15)

- **Conformal:** Tahmin olasılığına garantili güven kümesi ekle (Modül 15).
- **Bayesian:** Kazanma oranını Beta-Binom ile modelle; "gerçekten >0.5 olma
  olasılığı" (Modül 11). Sinyal güvenine göre pozisyon büyüklüğü ayarla.

---

## 9. Backtest gerçekçiliği (Modül 12)

Repodaki `src/backtest.py` ile stratejiyi simüle et — **ama**:
- İşlem maliyeti (komisyon + slippage) ekle. Çoğu "kârlı" backtest maliyetle ölür.
- Sharpe oranı, max drawdown, kazanma oranını raporla.
- **Out-of-sample** (modelin hiç görmediği dönem) test et.
- Parametre overfit'inden kaçın (Modül 04 çoklu test): 50 parametre deneyip en
  iyisini seçmek = gürültü ezberi.

---

## 10. Eleştirel değerlendirme (en önemli adım)

Kendine sor:
1. ✅ Hiç **veri sızıntısı** var mı? (Geleceğe bakan özellik? Tüm veride scale?)
2. ✅ **Baseline'ı** gerçekten yendim mi, anlamlı farkla mı (Modül 04)?
3. ✅ **Maliyetler** sonrası hâlâ kârlı mı?
4. ✅ Sonuç **birden çok dönemde** (rejimde) tutarlı mı, yoksa tek şanslı pencere mi?
5. ✅ Belirsizliği **dürüstçe** raporladım mı?
6. ✅ Bir nedensel iddiam var mı, varsa varsayımları geçerli mi (Modül 13)?

> 🔑 **Asıl ders:** İyi bir veri bilimcisini sıradan olandan ayıran şey, fancy
> model değil — **kendi sonucuna şüpheyle yaklaşıp onu kırmaya çalışmasıdır.**
> "Harika sonuç" çoğu zaman bir hatanın işaretidir.

---

## 🎓 Bitirme görevi

Yukarıdaki akışı baştan sona kendi kodunla, tek bir Jupyter notebook'ta uygula.
Sonunda 1 sayfalık bir rapor yaz:
- Hangi model kazandı, baseline'a göre ne kadar?
- Walk-forward AUC ve belirsizliği ne?
- En etkili 3 özellik (SHAP) ve mantıklı mı?
- Tespit ettiğin riskler/sızıntı şüpheleri.
- Bu modele gerçek parayla güvenir miydin? Neden (olmaz)?

Bunu yapabiliyorsan, müfredatı bitirdin — artık **istatistiksel düşünebiliyorsun**,
sadece formül uygulamıyorsun. 🎉

---

## ✅ Final kontrol listesi

- [ ] Veriyi çekip betimsel analiz yapabiliyorum (Modül 01-03).
- [ ] Sızıntısız özellik üretip zaman-bilinçli böldüm (Modül 05, 08).
- [ ] Baseline → lineer → boosting ilerleyişini kurdum (Modül 06-10).
- [ ] Walk-forward doğrulama ve dürüst metrik raporladım (Modül 08, 12).
- [ ] SHAP ile açıkladım, belirsizliği ekledim (Modül 11, 15).
- [ ] Sonuçlarımı eleştirel sorgulayabiliyorum.

← [Modül 15](15-modern-2026.md) · [Ana sayfaya dön](README.md)
