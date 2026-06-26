# Modül 10 — Gradient Boosting (XGBoost · LightGBM · CatBoost)

> **Hedef:** Tablo verisinde dünyanın en güçlü yöntemini derinlemesine öğrenmek.
> Kaggle yarışmalarının ve endüstri risk/öneri sistemlerinin çoğunu bunlar
> kazanır. Senin özellikle sorduğun **XGBoost** ve **CatBoost** burada.

> 📌 Ön koşul: Modül 09 (ağaçlar), Modül 07 (bias-variance, regularizasyon),
> Modül 08 (doğrulama). Boosting kolayca overfit eder — doğrulamayı iyi bilmelisin.

---

## 1. Boosting fikri: hataları sırayla düzelt

Random Forest ağaçları **bağımsız** eğitir (bagging). Boosting ise **sıralı**dır:

1. Basit bir ağaç kur — kötü tahmin yapar.
2. **Nerede yanıldığına** bak.
3. Yeni bir ağaç ekle: bu ağaç **kalan hatayı (residual)** düzeltmeye odaklanır.
4. Tekrarla — her ağaç öncekilerin hatalarını biraz daha azaltır.

> **Sezgi:** Tek başına zayıf "öğrenciler"i (sığ ağaçlar) bir takım hâline
> getirip, her birinin önceki takım arkadaşının hatasını telafi etmesini
> sağlamak. Yavaş yavaş, adım adım mükemmelleşme.

---

## 2. Gradient Boosting matematiği (sezgisel)

"Gradient" adı nereden geliyor? Her adımda, kayıp fonksiyonunun (loss)
**gradyanına** (en dik iniş yönüne) bir ağaç uydururuz:

$$F_{m}(x) = F_{m-1}(x) + \eta \cdot h_m(x)$$

- $F_{m-1}$ = şimdiye kadarki model.
- $h_m$ = yeni ağaç (kalan hatanın/gradyanın negatifine uyar).
- **η (learning rate / öğrenme oranı):** Her ağacın katkısını küçültür (örn.
  0.05). Küçük η + çok ağaç = daha iyi genelleme (ama yavaş). **En önemli
  hiperparametre.**

Regresyonda "kalan hata" = gerçek − tahmin. Sınıflandırmada gradyan,
log-loss'tan gelir. Genel çerçeve **her türevlenebilir kayıp** ile çalışır —
gücü buradan gelir.

---

## 3. Neden boosting, RF'i yener?

- RF **varyansı** düşürür ama her ağaç aynı şeyi öğrenmeye çalışır.
- Boosting **bias'ı** sistematik olarak düşürür — her ağaç yeni bir şey öğrenir.
- Sonuç: doğru ayarlandığında tablo verisinde **en yüksek doğruluk**.
- Bedeli: overfit'e daha yatkın, ayar (tuning) ister, sıralı olduğu için
  RF kadar kolay paralelleşmez.

---

## 4. Üç modern uygulama — kıyaslama

| | XGBoost | LightGBM | CatBoost |
|---|---|---|---|
| **Çıkış** | 2014 (Chen) | 2017 (Microsoft) | 2017 (Yandex) |
| **Ağaç büyütme** | Seviye bazlı (level-wise) | **Yaprak bazlı (leaf-wise)** | Simetrik (oblivious) |
| **Hız** | Hızlı | **En hızlı** (büyük veride) | Orta |
| **Bellek** | Orta | **Düşük** | Orta-yüksek |
| **Kategorik** | Elle kodlama gerekir | Yerel destek (belirt) | **En iyi yerel destek** |
| **Aşırı ayar** | Çok parametre | Kolayca overfit (yaprak bazlı) | **En iyi varsayılanlar** |
| **GPU** | Var | Var | **Çok iyi** |
| **En iyi olduğu yer** | Genel amaçlı, güvenilir | Büyük veri, hız kritik | Kategorik bol, az ayar isteyen |

> 🔑 **Pratik tavsiye:** Üçü de mükemmel. Başlangıç için **CatBoost** (en iyi
> varsayılanlar, kategorik kolaylığı), büyük veride **LightGBM** (hız), en yaygın
> ekosistem/dokümantasyon için **XGBoost**. Üçünü dene, doğrulamada kazananı seç.

---

## 5. XGBoost — sağlam çalışkan

XGBoost'un katkıları: ikinci dereceden (Newton) optimizasyon, **yerleşik L1/L2
regularizasyon**, eksik değer işleme, paralel/önbellekli verimli uygulama.

```python
import xgboost as xgb
from sklearn.metrics import roc_auc_score

model = xgb.XGBClassifier(
    n_estimators=1000,        # çok ağaç + early stopping ile gerçek sayıyı bul
    learning_rate=0.03,       # küçük η → iyi genelleme
    max_depth=4,              # sığ ağaçlar (boosting'de derinlik az olmalı)
    subsample=0.8,            # her ağaçta satırların %80'i (stokastik → regularize)
    colsample_bytree=0.8,     # her ağaçta sütunların %80'i
    reg_lambda=1.0,           # L2 ceza
    reg_alpha=0.0,            # L1 ceza
    min_child_weight=5,       # yaprak başına min ağırlık (overfit kontrolü)
    eval_metric="auc",
    early_stopping_rounds=50, # val skoru 50 turda iyileşmezse dur
    n_jobs=-1, random_state=0,
)
model.fit(X_tr, y_tr, eval_set=[(X_val, y_val)], verbose=False)
print("Test AUC:", roc_auc_score(y_te, model.predict_proba(X_te)[:, 1]))
print("Kullanılan ağaç sayısı:", model.best_iteration)
```

---

## 6. LightGBM — büyük veride hız şampiyonu

İki yenilik: **GOSS** (büyük gradyanlı örneklere odaklanma) ve **EFB** (seyrek
özellikleri birleştirme). **Yaprak bazlı** büyür: en çok kazanç veren yaprağı
böler → daha derin, daha doğru ama **overfit'e yatkın** (→ `num_leaves`'i kontrol et).

```python
import lightgbm as lgb

model = lgb.LGBMClassifier(
    n_estimators=2000,
    learning_rate=0.03,
    num_leaves=31,            # yaprak bazlı modelin KİLİT parametresi (< 2^max_depth)
    max_depth=-1,             # sınırsız ama num_leaves frenler
    subsample=0.8, subsample_freq=1,
    colsample_bytree=0.8,
    reg_lambda=1.0, reg_alpha=0.0,
    min_child_samples=30,     # yaprakta min örnek (overfit kontrolü)
    n_jobs=-1, random_state=0,
)
model.fit(
    X_tr, y_tr,
    eval_set=[(X_val, y_val)], eval_metric="auc",
    callbacks=[lgb.early_stopping(50), lgb.log_evaluation(0)],
)
# Kategorik özellikleri 'category' dtype yapıp categorical_feature ile verebilirsin
```

> ⚠️ LightGBM küçük veride (birkaç bin satır) kolayca overfit eder. `num_leaves`
> düşür, `min_child_samples` artır.

---

## 7. CatBoost — kategorik kralı, en iyi varsayılanlar

İki temel yeniliği:
- **Ordered Target Encoding:** Kategorik değişkenleri hedef sızıntısı OLMADAN
  kodlar (her örnek için sadece "geçmiş" örnekleri kullanır). Bu, manuel target
  encoding'in en büyük tuzağını (sızıntı) çözer.
- **Simetrik (oblivious) ağaçlar:** Her seviyede tüm dallar aynı bölmeyi kullanır
  → hızlı tahmin, doğal regularizasyon, az overfit.

```python
from catboost import CatBoostClassifier, Pool

# Kategorik sütunları SADECE isimle belirt — kodlamayı CatBoost halleder!
cat_features = ["parite", "saat_dilimi", "trend_durumu"]

model = CatBoostClassifier(
    iterations=2000,
    learning_rate=0.03,
    depth=6,                  # simetrik ağaç derinliği (6-10 tipik)
    l2_leaf_reg=3.0,          # L2 regularizasyon
    loss_function="Logloss",
    eval_metric="AUC",
    early_stopping_rounds=50,
    random_seed=0,
    verbose=0,
)
model.fit(
    X_tr, y_tr,
    cat_features=cat_features,         # 👈 elle one-hot YOK
    eval_set=(X_val, y_val),
)
print("Test AUC:", model.score(X_te, y_te))
```

> 💡 **Neden çok seviliyor:** Varsayılan ayarlarla bile çok iyi sonuç verir
> (az tuning), kategorik veriyi sihirli şekilde halleder, sızıntıya dirençlidir.
> Az deneyimliysen başlamak için en güvenli boosting kütüphanesi.

---

## 8. Hiperparametre ayarı — sistematik yaklaşım

**Önem sırasına göre** ayarla (en etkiliden başla):

1. **learning_rate + n_estimators:** Küçük lr (0.01–0.05) + early stopping.
   Bu ikili çifttir: lr düşürünce ağaç sayısı artmalı.
2. **Ağaç karmaşıklığı:** `max_depth` (XGB/CatBoost 4–8), `num_leaves` (LGBM).
3. **Örnekleme:** `subsample`, `colsample_bytree` (0.7–0.9) → stokastiklik,
   regularize eder.
4. **Regularizasyon:** `reg_lambda` (L2), `reg_alpha` (L1), `min_child_*`.

```python
# Optuna ile akıllı arama (grid'den çok daha verimli)
import optuna
def amac(trial):
    params = {
        "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.1, log=True),
        "max_depth": trial.suggest_int("max_depth", 3, 8),
        "subsample": trial.suggest_float("subsample", 0.6, 1.0),
        "colsample_bytree": trial.suggest_float("colsample_bytree", 0.6, 1.0),
        "reg_lambda": trial.suggest_float("reg_lambda", 1e-3, 10, log=True),
    }
    m = xgb.XGBClassifier(n_estimators=1000, early_stopping_rounds=50,
                          eval_metric="auc", **params)
    m.fit(X_tr, y_tr, eval_set=[(X_val, y_val)], verbose=False)
    return roc_auc_score(y_val, m.predict_proba(X_val)[:, 1])

study = optuna.create_study(direction="maximize")
study.optimize(amac, n_trials=50)
print("En iyi:", study.best_params)
```

> ⚠️ **Zaman serisinde** ayar ve early stopping için **TimeSeriesSplit** kullan
> (Modül 08). Rastgele bölme = sızıntı = sahte performans.

---

## 9. Yorumlama — SHAP (Modül 15'in önizlemesi)

Boosting "kara kutu" gibi görünür ama **SHAP** ile her tahminin nedenini
açıklayabilirsin:

```python
import shap
explainer = shap.TreeExplainer(model)
shap_values = explainer.shap_values(X_te)
shap.summary_plot(shap_values, X_te)   # hangi özellik, ne yönde, ne kadar etkili
```

SHAP, "bu işlemde neden AL dedi?" sorusunu özellik bazında cevaplar — güven ve
hata ayıklama için kritik.

---

## 10. Boosting tuzakları

- **Aşırı ağaç + yüksek lr = overfit.** Early stopping kullan, daima.
- **Hedef sızıntısı** na boosting çok duyarlıdır (gücü yüzünden sahte sinyali
  de mükemmel öğrenir). Modül 08'i ciddiye al.
- **Dengesiz sınıf:** `scale_pos_weight` (XGB), `class_weights` (CatBoost) ayarla.
- **Olasılık kalibrasyonu:** Ham çıktı bazen iyi kalibre değil — `CalibratedClassifierCV`.
- **Çok küçük veri:** Boosting parlamaz; regularize lineer model veya RF dene.

---

## 🎯 Alıştırma

1. BTC verisinde Modül 09'daki Random Forest'ı XGBoost ile değiştir. Aynı
   TimeSeriesSplit ile AUC'yi karşılaştır. Boosting kazandı mı?
2. Üç kütüphaneyi (XGBoost, LightGBM, CatBoost) varsayılan ayarlarla yarıştır.
   Hangisi kutudan çıktığı haliyle en iyi? Sonra Optuna ile XGBoost'u ayarla —
   ne kadar iyileşti?
3. SHAP summary plot çiz. Modelin en çok hangi göstergeye dayandığını ve yönünü
   yorumla. Mantıklı mı, yoksa sızıntı şüphesi var mı?

---

## ✅ Kontrol listesi

- [ ] Boosting'in (sıralı, hata düzeltme) bagging'den farkını biliyorum.
- [ ] learning_rate + n_estimators + early_stopping üçlüsünü anlıyorum.
- [ ] XGBoost/LightGBM/CatBoost'un ne zaman tercih edildiğini biliyorum.
- [ ] LightGBM'in yaprak-bazlı büyümesinin overfit riskini biliyorum.
- [ ] CatBoost'un kategorikleri nasıl sızıntısız kodladığını anlıyorum.
- [ ] Hiperparametreleri önem sırasıyla ayarlayabiliyorum.
- [ ] SHAP ile model açıklayabiliyorum.

Sonraki → [Modül 11: Bayesian İstatistik](11-bayesian.md)
