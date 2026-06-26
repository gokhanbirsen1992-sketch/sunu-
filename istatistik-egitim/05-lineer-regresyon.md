# Modül 05 — Lineer Regresyon

> **Hedef:** İstatistiğin ve makine öğrenmesinin **bel kemiği**. Bir sonucu
> (y) bir veya birden çok girdiyle (X) modellemek. Basit görünür ama tüm
> ileri yöntemler (GLM, regularizasyon, hatta sinir ağları) bunun üzerine kurulur.

---

## 1. Basit doğrusal regresyon

Tek girdi, tek çıktı arasında en iyi doğruyu çiz:
$$y = \beta_0 + \beta_1 x + \varepsilon$$

- **β₀ (kesişim):** x=0 iken y'nin değeri.
- **β₁ (eğim):** x bir birim artınca y ortalama ne kadar değişir. **Modelin
  kalbi budur.**
- **ε (hata terimi):** Modelin açıklayamadığı rastgelelik.

### En Küçük Kareler (OLS) — doğru nasıl bulunur?
"Hataların karelerinin toplamını" en küçük yapan β'ları seç:
$$\min_{\beta} \sum_{i=1}^{n} (y_i - \hat{y}_i)^2$$

Neden kare? (1) Negatif/pozitif hatalar birbirini götürmesin, (2) büyük
hataları daha çok cezalandırsın, (3) matematiksel olarak temiz kapalı çözüm verir.

---

## 2. Çoklu doğrusal regresyon

Birden çok girdi:
$$y = \beta_0 + \beta_1 x_1 + \beta_2 x_2 + \dots + \beta_p x_p + \varepsilon$$

Matris formunda kapalı çözüm (normal denklem):
$$\hat{\beta} = (X^T X)^{-1} X^T y$$

> **Katsayı yorumu (çok önemli):** βⱼ = "diğer tüm değişkenler **sabit
> tutulduğunda**, xⱼ bir birim artınca y'deki ortalama değişim." Bu "sabit
> tutma" gücü, regresyonu basit korelasyondan ayırır — kafa karıştırıcı
> faktörleri (confounder) kontrol etmeye başlarız (tam nedensellik için Modül 13).

---

## 3. Model ne kadar iyi? — R² ve arkadaşları

- **R² (belirleme katsayısı):** y'deki değişkenliğin yüzde kaçını model
  açıklıyor? 0–1 arası. R²=0.7 → "varyansın %70'ini açıklıyoruz."
- **Düzeltilmiş R² (Adjusted R²):** Gereksiz değişken eklemeyi cezalandırır.
  Çok değişkenli modelleri karşılaştırırken bunu kullan.
- **RMSE / MAE:** Tahmin hatasının ortalama büyüklüğü (y biriminde). Pratik
  doğruluk için R²'den daha somut.

> ⚠️ Yüksek R² "iyi model" garantisi değildir — overfit olabilir (Modül 08),
> ya da ilişki nedensel olmayabilir.

---

## 4. OLS'in 5 varsayımı (Gauss-Markov) — ihlal edersen ne olur?

Bunlar sağlanırsa OLS "en iyi yansız tahminci"dir (BLUE). İhlaller önemli:

1. **Doğrusallık:** y ile X arasındaki ilişki doğrusal. → Değilse: polinom/
   dönüşüm ekle veya doğrusal olmayan model (ağaç, Modül 09).
2. **Bağımsızlık:** Hatalar birbirinden bağımsız. → Zaman serisinde sıkça
   ihlal (otokorelasyon, Modül 12). Durbin-Watson testiyle bak.
3. **Homoskedastisite:** Hata varyansı sabit. → İhlal (heteroskedastisite):
   katsayılar yansız ama standart hatalar yanlış → "robust SE" kullan.
4. **Hataların normalliği:** ε ~ Normal. → Küçük örneklemde p-değerleri için
   gerekli; büyük örneklemde CLT kurtarır.
5. **Çoklu doğrusal bağıntı yok (multicollinearity):** Girdiler birbirinin
   kopyası olmamalı. → VIF (Variance Inflation Factor) > 5-10 ise sorun;
   regularizasyon (Modül 07) veya değişken atma çözer.

> 🔍 **Tanı grafikleri (residual plots):** Tahmin hatalarını (artıkları) çiz.
> - Artık vs tahmin: rastgele bulut olmalı (huni şekli = heteroskedastisite).
> - QQ-plot: artıklar doğru üzerinde olmalı (normallik).
> - Bir desen görüyorsan, model bir şeyi kaçırıyor demektir.

---

## 5. Python — iki yol

### statsmodels (istatistiksel yorum için — p-değeri, CI, tanı)
```python
import statsmodels.api as sm
import pandas as pd

X = df[["rsi", "hacim", "volatilite"]]
y = df["gelecek_getiri"]

X = sm.add_constant(X)          # kesişim terimi ekle
model = sm.OLS(y, X).fit()
print(model.summary())          # katsayılar, p-değerleri, R², CI hepsi burada
```

`summary()` çıktısında bak:
- **coef:** katsayılar (β).
- **P>|t|:** her katsayının p-değeri (anlamlı mı?).
- **R-squared / Adj. R-squared.**
- **[0.025 0.975]:** katsayıların %95 güven aralığı.

### scikit-learn (tahmin/ML pipeline için)
```python
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score

X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=42)
reg = LinearRegression().fit(X_tr, y_tr)
pred = reg.predict(X_te)
print("Test R²  :", r2_score(y_te, pred))
print("Test RMSE:", mean_squared_error(y_te, pred, squared=False))
```

> 📌 **statsmodels** = "neden" (çıkarım, yorum). **sklearn** = "tahmin"
> (pipeline, cross-validation). İkisini de öğren.

---

## 6. Özellik mühendisliği ve dönüşümler

Doğrusal model, *doğru özelliklerle beslenirse* şaşırtıcı derecede güçlüdür:
- **Etkileşim terimleri:** x₁·x₂ ("RSI'ın etkisi yüksek hacimde farklı mı?").
- **Polinom terimleri:** x² ile eğrisel ilişki yakala.
- **Log dönüşümü:** Çarpık değişkenleri (fiyat, hacim) düzleştir; katsayı
  "yüzde değişim" olarak yorumlanır.
- **Kukla değişkenler (one-hot):** Kategorikleri 0/1 sütunlara çevir.
- **Standartlaştırma:** Katsayıları karşılaştırmak ve regularizasyon için şart.

---

## 7. Sık tuzaklar

- **Aşırı yorum:** "x, y'yi *artırıyor*" demek nedensellik iddiasıdır —
  gözlemsel veride genelde yanlış. "İlişkili" de.
- **Ekstrapolasyon:** Modeli eğitim aralığının dışında kullanma (RSI 0–100
  gördün, sonra negatif RSI tahmin etme).
- **Veri sızıntısı:** Geleceği bilen bir özellik koyup "harika R²" almak.
  Zaman serisinde özellikle tehlikeli (Modül 08, 12).
- **Aykırı değerler:** Tek bir uç nokta tüm doğruyu çarpıtabilir; tanı
  grafikleriyle yakala (Cook's distance).

---

## 🎯 Alıştırma

1. BTC verisinde "yarınki getiri"yi bugünkü RSI, EMA farkı ve ATR ile OLS'le
   modelle. `summary()` çıktısını yorumla: hangi özellik anlamlı? R² ne?
2. Artık grafiklerini çiz. Homoskedastisite ve normallik varsayımları sağlanıyor
   mu? Huni şekli var mı?
3. Aynı modeli train/test bölüp sklearn ile kur. Test R²'si, eğitim R²'sinden
   ne kadar düşük? (Aradaki fark = overfit miktarı, Modül 08.)

---

## ✅ Kontrol listesi

- [ ] OLS'in neyi minimize ettiğini biliyorum (kareli hatalar).
- [ ] Katsayıyı "diğerleri sabitken" diye doğru yorumluyorum.
- [ ] 5 varsayımı ve ihlal sonuçlarını sayabiliyorum.
- [ ] Artık (residual) grafiklerini okuyabiliyorum.
- [ ] statsmodels (çıkarım) ile sklearn (tahmin) farkını biliyorum.

Sonraki → [Modül 06: Genelleştirilmiş Lineer Modeller (GLM)](06-glm-lojistik.md)
