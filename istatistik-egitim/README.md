# İstatistiksel Yöntemler — Sıfırdan 2026'ya Eksiksiz Müfredat

Bu kaynak, istatistiği **hiç bilmeyen** birinin adım adım ilerleyip
**2026'nın modern makine öğrenmesi ve nedensellik yöntemlerine** (XGBoost,
CatBoost, LightGBM, EconML, Bayesian, conformal prediction, TabPFN) kadar
ulaşmasını hedefler.

Her modül şu yapıyı izler:
1. **Sezgi** — konuyu günlük dille, neden var olduğunu anlatır.
2. **Matematik** — gerekli formüller (korkutmadan, açıklayarak).
3. **Python örneği** — çalıştırılabilir kod.
4. **Tuzaklar** — sık yapılan hatalar.
5. **Alıştırma** — kendi başına denemen için.

> ⚠️ Bu materyal eğitim amaçlıdır. Finansal/tıbbi karar için tek başına
> yeterli değildir.

---

## 📚 Öğrenme Yol Haritası

Modülleri **sırayla** çalış. Her biri öncekine dayanır. Atlamak istersen
"Ön koşul" sütununa bak.

| # | Modül | Konu | Ön koşul | Zorluk |
|---|---|---|---|---|
| 01 | [Betimsel İstatistik](01-betimsel-istatistik.md) | Ortalama, medyan, varyans, korelasyon, görselleştirme | Yok | 🟢 |
| 02 | [Olasılık Teorisi](02-olasilik-teorisi.md) | Olasılık, koşullu olasılık, Bayes kuralı, beklenen değer | 01 | 🟢 |
| 03 | [Olasılık Dağılımları](03-olasilik-dagilimlari.md) | Normal, binom, Poisson, üstel, CLT | 02 | 🟢 |
| 04 | [Çıkarımsal İstatistik](04-cikarimsal-istatistik.md) | Tahmin, güven aralığı, hipotez testi, p-değeri, güç | 03 | 🟡 |
| 05 | [Lineer Regresyon](05-lineer-regresyon.md) | OLS, varsayımlar, tanı grafikleri, yorumlama | 04 | 🟡 |
| 06 | [Genelleştirilmiş Lineer Modeller (GLM)](06-glm-lojistik.md) | Lojistik, Poisson, link fonksiyonları | 05 | 🟡 |
| 07 | [Regularizasyon](07-regularizasyon.md) | Ridge, Lasso, Elastic Net, bias-variance | 05 | 🟡 |
| 08 | [Model Değerlendirme](08-model-degerlendirme.md) | Cross-validation, metrikler, overfitting, data leakage | 05 | 🟡 |
| 09 | [Ağaç Tabanlı Yöntemler](09-agac-tabanli.md) | Karar ağacı, bagging, Random Forest | 08 | 🟡 |
| 10 | [Gradient Boosting](10-gradient-boosting.md) | GBM, **XGBoost, LightGBM, CatBoost** derinlemesine | 09 | 🔴 |
| 11 | [Bayesian İstatistik](11-bayesian.md) | Prior/posterior, MCMC, PyMC, hiyerarşik modeller | 04 | 🔴 |
| 12 | [Zaman Serisi](12-zaman-serisi.md) | ARIMA, GARCH, Prophet, durağanlık | 05 | 🔴 |
| 13 | [Nedensellik & EconML](13-nedensellik-econml.md) | Causal inference, DML, IV, DiD, uplift, **EconML** | 05, 10 | 🔴 |
| 14 | [Denetimsiz Öğrenme](14-denetimsiz-ogrenme.md) | PCA, t-SNE/UMAP, k-means, DBSCAN, GMM | 03 | 🟡 |
| 15 | [Modern & 2026 Yöntemleri](15-modern-2026.md) | Tabular DL, TabPFN, conformal, AutoML, SHAP | 10 | 🔴 |
| 16 | [Uçtan Uca Proje](16-proje.md) | Trading verisiyle gerçek pipeline | Hepsi | 🔴 |

🟢 Başlangıç · 🟡 Orta · 🔴 İleri

---

## 🗓️ Önerilen Takvim

Haftada ~6-8 saat ayırırsan:

- **1. Ay — Temeller:** Modül 01–04. İstatistiğin "neden"ini öğren.
- **2. Ay — Regresyon ailesi:** Modül 05–08. Tahmin modellemenin bel kemiği.
- **3. Ay — Makine öğrenmesi:** Modül 09–10. Ağaçlar ve boosting (Kaggle'ın kralı).
- **4. Ay — İleri konular:** Modül 11–13. Bayesian, zaman serisi, nedensellik.
- **5. Ay — Modern + uygulama:** Modül 14–16. 2026 teknikleri ve gerçek proje.

Acelen varsa **hızlı yol**: 01 → 04 → 05 → 08 → 10 → 16.

---

## 🧰 Kurulum

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install numpy pandas scipy matplotlib seaborn scikit-learn \
            statsmodels xgboost lightgbm catboost pymc arviz \
            econml shap prophet
```

Python 3.10+ önerilir. Her modülün kod örnekleri bu paketlerle çalışır.

---

## 🧭 Nasıl Çalışmalı?

1. **Önce sezgiyi anla, formülü ezberleme.** Formül sezginin kısaltmasıdır.
2. **Kodu kendi verinle çalıştır.** Bu repodaki trading botunun (BTC/USDT)
   verisi mükemmel bir oyun alanıdır — Modül 16'da kullanıyoruz.
3. **Her modül sonundaki alıştırmayı yap.** Okumak ≠ öğrenmek.
4. **Hata yap.** Overfit et, yanlış test seç, sonra düzelt. En iyi öğretmen budur.

---

## 📖 Sözlük (hızlı başvuru)

| Terim | Açıklama |
|---|---|
| **Özellik (feature)** | Modele giren girdi değişkeni (X) |
| **Hedef (target)** | Tahmin etmeye çalıştığımız çıktı (y) |
| **Overfitting** | Modelin eğitim verisini ezberleyip yeni veride başarısız olması |
| **Bias-Variance** | Yanlılık (basitlik) ile varyans (aşırı karmaşıklık) dengesi |
| **Hiperparametre** | Modelin öğrenmeden önce elle ayarlanan ayarı (örn. ağaç derinliği) |
| **Çapraz doğrulama** | Veriyi parçalara bölüp her parçada test ederek dürüst başarı ölçümü |
| **p-değeri** | Gözlenen sonucun şans eseri olma olasılığının ölçüsü |
| **Prior / Posterior** | Bayesian'da veri öncesi / sonrası inanç |

---

Başlamak için → [Modül 01: Betimsel İstatistik](01-betimsel-istatistik.md)
