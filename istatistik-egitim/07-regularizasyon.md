# Modül 07 — Regularizasyon (Ridge, Lasso, Elastic Net)

> **Hedef:** Modelin **ezberlemesini (overfitting)** engellemek, çok sayıda
> özellikle başa çıkmak ve otomatik özellik seçimi yapmak. Modern ML'in
> vazgeçilmez aracı.

---

## 1. Bias-Variance dengesi — tüm ML'in kalbi

Bir modelin test hatası iki bileşene ayrılır:

- **Bias (yanlılık):** Model çok basit → gerçek deseni kaçırır
  (**underfitting**). Örn. eğrisel veriye düz çizgi.
- **Variance (varyans):** Model çok karmaşık → eğitim verisindeki gürültüyü
  ezberler (**overfitting**). Yeni veride çöker.

$$\text{Test Hatası} = \text{Bias}^2 + \text{Variance} + \text{İndirgenemez gürültü}$$

> 🔑 İkisini aynı anda sıfırlayamazsın — **denge** kurarsın. Regularizasyon,
> bilerek biraz bias ekleyip varyansı çok düşürerek toplam hatayı azaltır.

```
Hata
 │ \                          /  ← Variance (karmaşıklıkla artar)
 │  \                       /
 │   \___ Toplam ___      /
 │        \        \    /
 │  Bias ↓ \________ \/_____  ← en iyi nokta (denge)
 │                  /\
 └──────────────────────────► Model karmaşıklığı
```

---

## 2. Regularizasyon fikri: katsayıları cezalandır

OLS sadece hatayı küçültür. Regularizasyon, **büyük katsayıları da cezalandıran**
bir terim ekler — model "abartmasın" diye:

$$\min_{\beta} \underbrace{\sum (y_i - \hat{y}_i)^2}_{\text{uyum}} + \underbrace{\lambda \cdot \text{ceza}(\beta)}_{\text{basitlik}}$$

**λ (lambda):** Cezanın gücü (hiperparametre). λ=0 → sıradan OLS. λ→∞ → tüm
katsayılar 0'a yaklaşır (aşırı basit). Doğru λ'yı cross-validation seçer.

---

## 3. Üç ana yöntem

### Ridge (L2) — katsayıları küçültür
$$\text{ceza} = \lambda \sum \beta_j^2$$
- Katsayıları 0'a **yaklaştırır ama tam 0 yapmaz**.
- **Çoklu doğrusal bağıntıda (multicollinearity)** harika — korele
  değişkenler arasında ağırlığı paylaştırır.
- Tüm özellikleri tutar.

### Lasso (L1) — otomatik özellik seçimi
$$\text{ceza} = \lambda \sum |\beta_j|$$
- Bazı katsayıları **tam olarak 0** yapar → **gereksiz özellikleri eler**.
- Yüzlerce özellikten önemli olanları otomatik seçer → **seyrek (sparse)** model.
- Korele özelliklerden genelde birini seçip diğerini atar (rastgele olabilir).

### Elastic Net — ikisinin karışımı
$$\text{ceza} = \lambda \left( \alpha \sum |\beta_j| + (1-\alpha)\sum \beta_j^2 \right)$$
- L1 ve L2'nin avantajlarını birleştirir.
- **Korele özellik gruplarında** Lasso'dan iyi: grubu birlikte tutar/atar.
- Çok özellikli, korele veride genelde en iyi varsayılan seçimdir.

| | Katsayıyı 0 yapar mı? | En iyi ne zaman? |
|---|---|---|
| **Ridge** | Hayır (küçültür) | Tüm özellikler az çok faydalı, multicollinearity var |
| **Lasso** | Evet (eler) | Çok özellik, çoğu gereksiz, seyreklik isteniyor |
| **Elastic Net** | Evet (gruplar) | Çok ve korele özellik (genel güvenli seçim) |

---

## 4. KRİTİK: önce standartlaştır!

Regularizasyon katsayının büyüklüğünü cezalandırır. Eğer bir özellik
"liralarla", diğeri "yüzdelerle" ölçülmüşse, ceza adaletsiz olur.
**Her zaman özellikleri ölçekle** (StandardScaler).

```python
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import RidgeCV, LassoCV, ElasticNetCV
from sklearn.pipeline import make_pipeline
import numpy as np

# RidgeCV: en iyi λ'yı (alpha) çapraz doğrulamayla otomatik seçer
ridge = make_pipeline(
    StandardScaler(),
    RidgeCV(alphas=np.logspace(-3, 3, 50))
).fit(X_tr, y_tr)

lasso = make_pipeline(
    StandardScaler(),
    LassoCV(alphas=np.logspace(-3, 1, 50), cv=5, max_iter=10000)
).fit(X_tr, y_tr)

# Lasso hangi özellikleri sıfırladı (eledi)?
coefs = lasso.named_steps["lassocv"].coef_
print("Elenen özellik sayısı:", np.sum(coefs == 0))
```

> ⚠️ Scaler'ı **pipeline içine koy** ki ölçekleme parametreleri sadece eğitim
> verisinden öğrenilsin. Tüm veride scale edip sonra bölersen **veri sızıntısı**
> olur (Modül 08).

---

## 5. Lojistik regresyonda regularizasyon

scikit-learn'de `LogisticRegression` **varsayılan olarak L2 regularize**dir!
`C` parametresi = 1/λ → **küçük C = güçlü ceza.**

```python
from sklearn.linear_model import LogisticRegressionCV
clf = LogisticRegressionCV(Cs=10, penalty="l1", solver="liblinear", cv=5)
clf.fit(X_tr, y_tr)
```

---

## 6. Ne zaman regularizasyon, ne zaman ağaç?

- **Çok sayıda özellik, az gözlem (p > n):** Lasso/Elastic Net parlar
  (genomik, metin, çok faktörlü finans).
- **Yorumlanabilirlik isteniyor:** Lasso seyrek, açıklanabilir model verir.
- **Doğrusal olmayan karmaşık etkileşimler:** Regularize lineer model yetmez →
  Gradient Boosting (Modül 10). Boosting'in kendi regularizasyonu vardır.

> 💡 Modern pratik: Önce **regularize lineer model** kur (güçlü, hızlı, yorumlanır
> bir taban çizgisi). Sonra **gradient boosting** ile geç. Aradaki fark, doğrusal
> olmayanlığın değerini gösterir.

---

## 🎯 Alıştırma

1. BTC verisinde 15+ teknik gösterge üret (farklı periyotlarda RSI, EMA, MACD,
   Bollinger genişliği, momentum...). OLS ile overfit gözlemle (eğitim R² >>
   test R²).
2. Aynı özelliklerle Ridge, Lasso ve Elastic Net kur (CV ile λ seç). Test
   performansları OLS'ten iyi mi?
3. Lasso hangi göstergeleri sıfırladı? Geriye kalanlar mantıklı mı? Bu, otomatik
   özellik seçimidir — yorumla.

---

## ✅ Kontrol listesi

- [ ] Bias-variance dengesini bir cümleyle açıklayabiliyorum.
- [ ] Ridge (küçültür) ile Lasso (eler) farkını biliyorum.
- [ ] Elastic Net'in ne zaman tercih edildiğini biliyorum.
- [ ] Regularizasyondan önce standartlaştırmanın şart olduğunu biliyorum.
- [ ] λ'nın (C) cross-validation ile seçildiğini anlıyorum.

Sonraki → [Modül 08: Model Değerlendirme](08-model-degerlendirme.md)
