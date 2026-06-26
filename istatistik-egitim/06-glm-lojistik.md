# Modül 06 — Genelleştirilmiş Lineer Modeller (GLM)

> **Hedef:** Lineer regresyonu, çıktının sürekli olmadığı durumlara
> (evet/hayır, sayım, oran) genişletmek. **Lojistik regresyon** — sınıflandırmanın
> temeli — burada öğrenilir.

---

## 1. Neden GLM'e ihtiyaç var?

OLS, y'nin sürekli ve (−∞, +∞) arası olduğunu varsayar. Ama:
- "Yarın yükselir mi?" → y ∈ {0, 1} (ikili). OLS olasılığı 1'in üstüne/0'ın
  altına taşırabilir — saçma.
- "Günde kaç işlem?" → y ∈ {0, 1, 2, ...} (sayım, negatif olamaz).

**GLM** üç parçayla bunu çözer:
1. **Rastgele bileşen:** y'nin dağılımı (normal, binom, Poisson...).
2. **Doğrusal tahminci:** η = β₀ + β₁x₁ + ... (her zaman aynı).
3. **Link fonksiyonu:** η'yı y'nin ortalamasına bağlayan dönüşüm.

| Çıktı tipi | Dağılım | Link | Model adı |
|---|---|---|---|
| Sürekli | Normal | kimlik | Lineer regresyon (Modül 05) |
| İkili (0/1) | Binom | logit | **Lojistik regresyon** |
| Sayım | Poisson | log | **Poisson regresyon** |
| Sayım (aşırı yayılım) | Negatif binom | log | NB regresyon |

---

## 2. Lojistik Regresyon — en önemli sınıflandırıcı

İkili sonucun olasılığını modeller. Doğrusal kombinasyonu **sigmoid** ile
0–1 arasına sıkıştırır:

$$P(y=1 \mid x) = \sigma(\beta_0 + \beta_1 x_1 + \dots) = \frac{1}{1 + e^{-(\beta_0 + \beta_1 x + \dots)}}$$

Sigmoid eğrisi "S" şeklindedir: çok küçük η → 0'a, çok büyük η → 1'e yaklaşır.

### Odds ve katsayı yorumu
- **Odds (bahis oranı):** P / (1−P). "Olma şansının olmama şansına oranı."
- Lojistik regresyon aslında **log-odds**'u doğrusal modeller:
  $$\log\frac{P}{1-P} = \beta_0 + \beta_1 x_1 + \dots$$
- **Yorum:** xⱼ bir birim artınca, odds **e^βⱼ kat** değişir. e^β = **odds oranı
  (OR)**. OR=2 → "bu özellik olayın bahsini 2 katına çıkarır."

### Nasıl tahmin edilir? — Maksimum Olabilirlik (MLE)
OLS'teki "kareli hata" yerine, gözlenen veriyi en olası kılan β'ları buluruz
(log-likelihood'u maksimize). Sınıflandırmada kayıp fonksiyonu **log-loss /
cross-entropy**'dir.

```python
import statsmodels.api as sm
import numpy as np

X = sm.add_constant(df[["rsi", "hacim_z", "trend"]])
y = df["yukseldi_mi"]   # 0/1

logit = sm.Logit(y, X).fit()
print(logit.summary())

# Odds oranları (yorumlanabilir)
print("Odds oranları:\n", np.exp(logit.params))
```

### scikit-learn versiyonu (pipeline için)
```python
from sklearn.linear_model import LogisticRegression
clf = LogisticRegression(max_iter=1000, C=1.0)  # C = 1/regularizasyon
clf.fit(X_tr, y_tr)
proba = clf.predict_proba(X_te)[:, 1]   # olasılık çıktısı (ham etiket değil!)
```

> 💡 Olasılık çıktısı (`predict_proba`) ham 0/1 etiketten çok daha değerlidir:
> eşiği (threshold) işine göre ayarlarsın. Trading'de "%51 yükseliş" ile
> "%95 yükseliş" çok farklı işlem büyüklüğü demektir.

---

## 3. Sınıflandırma metrikleri (Modül 08'in önizlemesi)

Accuracy (doğruluk) **yanıltıcıdır** — özellikle dengesiz veride. %95'i "hayır"
olan veride her şeye "hayır" diyen model %95 doğru ama işe yaramaz.

- **Confusion matrix:** TP, FP, TN, FN.
- **Precision:** "AL dediklerimin kaçı gerçekten yükseldi?" (yanlış alarm maliyeti).
- **Recall (duyarlılık):** "Gerçek yükselişlerin kaçını yakaladım?" (kaçırma maliyeti).
- **F1:** Precision ve recall'un harmonik ortalaması.
- **ROC-AUC:** Eşikten bağımsız ayırt etme gücü (0.5=şans, 1.0=mükemmel).
- **PR-AUC:** Dengesiz veride ROC-AUC'tan daha bilgilendirici.

---

## 4. Poisson Regresyon — sayımlar için

"Günde kaç sinyal?", "saatte kaç işlem?" gibi negatif olmayan tam sayılar.
$$\log(E[y]) = \beta_0 + \beta_1 x_1 + \dots \quad\Rightarrow\quad E[y] = e^{\beta_0 + \beta_1 x + \dots}$$

Katsayı yorumu: xⱼ bir birim artınca beklenen sayım **e^βⱼ kat** değişir.

> ⚠️ Poisson varsayımı: ortalama = varyans. Gerçekte varyans çok daha büyükse
> ("aşırı yayılım"), **Negatif Binom regresyon** kullan — aksi halde standart
> hataların yanlış olur.

```python
import statsmodels.api as sm
pois = sm.GLM(y_sayim, X, family=sm.families.Poisson()).fit()
print(pois.summary())
```

---

## 5. Diğer faydalı GLM/uzantılar

- **Multinomial lojistik:** 3+ sınıf (AL / SAT / BEKLE).
- **Ordinal lojistik:** Sıralı sonuç (düşük/orta/yüksek risk).
- **Gamma regresyon:** Pozitif sürekli, çarpık (hasar tutarı, süre).
- **Tobit:** Sansürlü/sınırlı çıktı.

---

## 🎯 Alıştırma

1. BTC verisinde "yarın yükseldi mi?" (1/0) hedefini RSI, trend ve hacimle
   lojistik regresyonla modelle. Odds oranlarını yorumla: hangi özellik
   yükseliş bahsini en çok artırıyor?
2. ROC-AUC ve PR-AUC hesapla. Model rastgeleden (0.5) iyi mi?
3. `predict_proba` çıktısının eşiğini 0.5'ten 0.6'ya çıkar. Precision ve recall
   nasıl değişiyor? Trading için hangi eşik daha mantıklı?

---

## ✅ Kontrol listesi

- [ ] GLM'in 3 parçasını (dağılım, doğrusal tahminci, link) biliyorum.
- [ ] Lojistik regresyonun neden olasılık çıktığını (sigmoid) anlıyorum.
- [ ] Odds oranını (e^β) yorumlayabiliyorum.
- [ ] Accuracy'nin neden yanıltıcı olduğunu, precision/recall/AUC'u biliyorum.
- [ ] Sayım verisi için Poisson/NB regresyonu seçebiliyorum.

Sonraki → [Modül 07: Regularizasyon](07-regularizasyon.md)
