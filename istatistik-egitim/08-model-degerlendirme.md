# Modül 08 — Model Değerlendirme ve Doğrulama

> **Hedef:** "Modelim iyi mi?" sorusuna **dürüstçe** cevap vermek. Bu modül,
> kötü modeli "harika" sanmaktan seni kurtarır — ve trading'de bu, para demektir.

> 🔑 **Altın kural:** Bir modeli ASLA üzerinde eğitildiği veriyle değerlendirme.
> Sınava soruları önceden vererek hazırlanan öğrenci gibi — gerçek dünyada çöker.

---

## 1. Train / Validation / Test ayrımı

Veriyi üçe böl:
- **Eğitim (train):** Model katsayılarını öğrenir (~%60-70).
- **Doğrulama (validation):** Hiperparametre seçer, model karşılaştırırsın (~%15-20).
- **Test (holdout):** **Sadece bir kez**, en sonda, gerçek performansı ölçer (~%15-20).

> Test setine sürekli bakıp model ayarlarsan, dolaylı olarak ona overfit edersin.
> Test seti "kasada kilitli" kalmalı.

---

## 2. Çapraz Doğrulama (Cross-Validation)

Tek bir train/val bölmesi şanslı/şanssız olabilir. **k-fold CV** veriyi k parçaya
böler; her seferinde 1 parça doğrulama, k−1 parça eğitim — k kez döner, ortalama
alır. Daha kararlı ve dürüst tahmin.

```python
from sklearn.model_selection import cross_val_score
import numpy as np
scores = cross_val_score(model, X, y, cv=5, scoring="roc_auc")
print(f"AUC: {scores.mean():.3f} ± {scores.std():.3f}")
```

- **Stratified k-fold:** Sınıflandırmada her parçada sınıf oranını korur
  (dengesiz veride şart).
- **LOOCV (leave-one-out):** k=n. Küçük veride; pahalı.

---

## 3. ⏰ Zaman serisinde CV — DİKKAT!

> **Trading'in en ölümcül hatası:** Sıradan k-fold CV zaman serisinde
> **GELECEĞİ KULLANARAK GEÇMİŞİ TAHMİN EDER** → veri sızıntısı → gerçek dışı
> harika sonuçlar → canlıda çöküş.

Çözüm: zamanı koruyan bölme.

```python
from sklearn.model_selection import TimeSeriesSplit
tscv = TimeSeriesSplit(n_splits=5)   # her fold geçmişle eğitir, gelecekle test eder
for train_idx, test_idx in tscv.split(X):
    # train_idx HER ZAMAN test_idx'ten önceki zamanlar
    ...
```

- **Walk-forward (ileri yürüyen) doğrulama:** Pencereyi zamanla kaydır;
  gerçek alım-satımı en iyi taklit eden yöntem.
- **Purging & embargo:** Eğitim ve test arasına boşluk koy ki örtüşen
  etiketler sızmasın (Lopez de Prado'nun finansal ML yöntemi).

---

## 4. Veri Sızıntısı (Data Leakage) — sessiz katil

Modelin, tahmin anında **gerçekte sahip olmayacağı** bilgiyi görmesi. İyi
sonuçlar verir ama sahtedir. Sık kaynaklar:

- **Geleceğe bakan özellik:** "Gelecek 5 günün ortalaması" gibi bir özellik.
- **Tüm veride ölçekleme/doldurma:** Scaler'ı/imputer'ı bölmeden ÖNCE tüm
  veriye uydurmak → test bilgisi eğitime sızar. **Pipeline kullan.**
- **Hedef sızıntısı:** Sonucu zaten içeren bir değişken (örn. "kapanış fiyatı"
  ile "getiri"yi tahmin etmek).
- **Çoğaltılmış/örtüşen örnekler:** Aynı olayın train ve test'te olması.

> 🔍 Sezgini bozan test: Sonuçların "çok iyi"yse, muhtemelen sızıntı vardır.
> Şüpheci ol.

---

## 5. Regresyon metrikleri

| Metrik | Anlam | Not |
|---|---|---|
| **MAE** | Ortalama mutlak hata | Yorumu kolay, aykırıya dayanıklı |
| **RMSE** | Kareli hatanın kökü | Büyük hataları daha çok cezalandırır |
| **R²** | Açıklanan varyans oranı | Ölçekten bağımsız, kıyas için |
| **MAPE** | Ortalama yüzde hata | y≈0 olduğunda patlar, dikkat |

---

## 6. Sınıflandırma metrikleri (derinlemesine)

**Confusion matrix** her şeyin temeli:

|  | Tahmin: Pozitif | Tahmin: Negatif |
|---|---|---|
| **Gerçek: Pozitif** | TP | FN (kaçırma) |
| **Gerçek: Negatif** | FP (yanlış alarm) | TN |

- **Precision = TP/(TP+FP):** Pozitif dediklerimin doğruluğu. *Yanlış alarm
  pahalıysa* (gereksiz işlem komisyonu) buna odaklan.
- **Recall = TP/(TP+FN):** Gerçek pozitifleri yakalama. *Kaçırmak pahalıysa*
  (büyük fırsatı kaçırmak) buna odaklan.
- **F1:** İkisinin dengesi.
- **ROC-AUC:** Tüm eşiklerde ayırt etme gücü. Dengeli veride iyi.
- **PR-AUC:** Dengesiz veride (nadir olay) ROC-AUC'tan üstün.
- **Log-loss:** Olasılık kalibrasyonunu cezalandırır.

> Trading'de metrik **işine** bağlı: yüksek precision'lı az ama isabetli sinyal mi,
> yoksa yüksek recall'lı çok sinyal mi? İş hedefini metriğe çevir.

---

## 7. Olasılık kalibrasyonu

Model "%70 yükseliş" diyorsa, gerçekten bu durumların ~%70'i yükselmeli.
Aksi halde olasılıklar yalan söyler (pozisyon büyüklüğü hesabın bozulur).
- **Reliability diagram** ile kontrol et.
- `CalibratedClassifierCV` (Platt scaling / isotonic) ile düzelt.

---

## 8. Baseline (taban çizgisi) olmadan rakam okuma

Her zaman **aptal bir referans** ile karşılaştır:
- Regresyonda: "her zaman ortalamayı tahmin et."
- Sınıflandırmada: "her zaman çoğunluk sınıfını tahmin et."
- Zaman serisinde: "yarın = bugün" (naive forecast).

Modelin baseline'ı yenmiyor mu? O zaman karmaşıklık boşa.

---

## 9. Bütünleşik doğru iş akışı

```python
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import GridSearchCV, TimeSeriesSplit
from sklearn.linear_model import LogisticRegression

pipe = Pipeline([
    ("scaler", StandardScaler()),          # sızıntısız: fold içinde fit
    ("clf", LogisticRegression(max_iter=1000)),
])
param_grid = {"clf__C": [0.01, 0.1, 1, 10]}

# Zaman serisi için TimeSeriesSplit!
grid = GridSearchCV(pipe, param_grid, cv=TimeSeriesSplit(5), scoring="roc_auc")
grid.fit(X_train, y_train)

print("En iyi C:", grid.best_params_)
print("CV AUC :", grid.best_score_)
# SADECE şimdi, en sonda, kilitli test setine bak:
print("Test AUC:", grid.score(X_test, y_test))
```

---

## 🎯 Alıştırma

1. Modül 07'deki çok-özellikli modeli hem sıradan KFold hem TimeSeriesSplit ile
   değerlendir. Sıradan KFold neden gerçekçi olmayan derecede iyi çıkıyor?
   (Sızıntıyı gör.)
2. Bir özelliği kasten "geleceğe bakar" hale getir (örn. yarının fiyatı).
   AUC'nin nasıl 0.99'a fırladığını gözlemle — klasik sızıntı imzası.
3. Modelini naive baseline ("yarın=bugün yönü") ile karşılaştır. Gerçekten
   ek değer katıyor mu?

---

## ✅ Kontrol listesi

- [ ] Train/val/test rollerini ve test setini "kilitli tutmayı" biliyorum.
- [ ] k-fold CV'nin neden tek bölmeden iyi olduğunu anlıyorum.
- [ ] Zaman serisinde neden TimeSeriesSplit/walk-forward şart olduğunu biliyorum.
- [ ] En az 4 veri sızıntısı kaynağı sayabiliyorum.
- [ ] İşime uygun metriği (precision vs recall vs AUC) seçebiliyorum.
- [ ] Her modeli bir baseline ile kıyaslıyorum.

Sonraki → [Modül 09: Ağaç Tabanlı Yöntemler](09-agac-tabanli.md)
