# Modül 09 — Ağaç Tabanlı Yöntemler

> **Hedef:** Karar ağaçları, bagging ve Random Forest. Bunlar hem güçlü hem
> yorumlanabilir, hem de Modül 10'daki **gradient boosting**'in temelini oluşturur.

---

## 1. Karar Ağacı (Decision Tree)

Veriyi ardışık "evet/hayır" sorularıyla bölen akış şeması:

```
RSI < 30 ?
├── Evet → Trend yükseliş mi?
│         ├── Evet → AL  (yaprak)
│         └── Hayır → BEKLE
└── Hayır → RSI > 70 ?
          ├── Evet → SAT
          └── Hayır → BEKLE
```

### Nasıl bölünür? — saflık (purity) ölçüleri
Her bölmede, çocuk düğümleri olabildiğince "saf" (tek sınıf) yapan özellik+eşik
seçilir:
- **Gini saflığı:** Sınıflandırmada (CART). Düşük = saf.
- **Entropi / Bilgi kazancı (Information Gain):** Bilgi teorisinden.
- **Varyans azaltma:** Regresyonda (yapraktaki değerlerin varyansını düşür).

### Avantajları
- **Yorumlanabilir** (kuralları görebilirsin — "white box").
- Ölçeklemeye/dönüşüme **ihtiyaç duymaz**.
- Doğrusal olmayan ilişkileri ve **etkileşimleri** otomatik yakalar.
- Kategorik + sayısal veriyi birlikte işler.

### En büyük zaafı: overfitting
Tek bir ağaç, derinleşince eğitim verisini ezberler (her yaprakta 1 örnek).
Çözüm: **budama (pruning)**, `max_depth`, `min_samples_leaf` ile sınırla — VEYA
çok sayıda ağacı birleştir (sonraki bölümler).

```python
from sklearn.tree import DecisionTreeClassifier, plot_tree
import matplotlib.pyplot as plt

tree = DecisionTreeClassifier(max_depth=3, min_samples_leaf=20, random_state=0)
tree.fit(X_tr, y_tr)
plt.figure(figsize=(16, 8))
plot_tree(tree, feature_names=X.columns, filled=True, class_names=["SAT","AL"])
plt.savefig("agac.png")
```

---

## 2. Ensemble fikri: "kalabalığın bilgeliği"

Tek bir ağaç gürültülüdür. Ama **çok sayıda farklı ağacın oyunu birleştirilirse**
hatalar birbirini götürür. İki ana strateji:

- **Bagging (paralel):** Ağaçları bağımsız, paralel eğit, ortalama al →
  **varyansı düşürür**. (Random Forest)
- **Boosting (sıralı):** Ağaçları sırayla eğit, her biri öncekinin hatasını
  düzeltsin → **bias'ı düşürür**. (Modül 10)

---

## 3. Bagging (Bootstrap Aggregating)

1. Eğitim verisinden **bootstrap** (yerine koyarak rastgele) örneklemler çek.
2. Her örnekleme bir ağaç eğit.
3. Tahminleri ortalama (regresyon) / oy çokluğu (sınıflandırma) ile birleştir.

Tek tek ağaçlar overfit etse de, ortalamaları kararlıdır.

---

## 4. Random Forest — bagging + ekstra rastgelelik

Random Forest, bagging'e bir hile ekler: **her bölmede özelliklerin sadece
rastgele bir alt kümesine** bakar. Bu, ağaçları birbirinden **ilişkisizleştirir**
(decorrelation) — güçlü bir özellik tüm ağaçlara hükmedemez, çeşitlilik artar,
ensemble daha da güçlenir.

```python
from sklearn.ensemble import RandomForestClassifier
rf = RandomForestClassifier(
    n_estimators=400,      # ağaç sayısı (çok = iyi ama yavaş; doygunlaşır)
    max_features="sqrt",   # her bölmede bakılacak özellik sayısı (RF'in sırrı)
    max_depth=None,        # ağaçlar derin (ensemble overfit'i dengeler)
    min_samples_leaf=5,
    n_jobs=-1, random_state=0,
).fit(X_tr, y_tr)
```

### Önemli özellikler
- **OOB (Out-of-Bag) skoru:** Her ağaç, görmediği örneklerle test edilir →
  bedava çapraz doğrulama. `oob_score=True`.
- **Özellik önemi (feature importance):** Hangi değişken ne kadar katkı yaptı.
  ⚠️ Varsayılan "impurity importance" yüksek kardinaliteli/korele özellikleri
  şişirir — **permütasyon önemi** veya **SHAP** (Modül 15) daha güvenilir.

```python
import pandas as pd
from sklearn.inspection import permutation_importance
imp = permutation_importance(rf, X_te, y_te, n_repeats=10, random_state=0)
print(pd.Series(imp.importances_mean, index=X.columns).sort_values(ascending=False))
```

---

## 5. Random Forest avantaj/dezavantaj

✅ Güçlü "kutudan çıkar çıkmaz" performans, az ayar gerektirir.
✅ Overfit'e bagging'den dolayı dirençli.
✅ Özellik önemi verir, eksik değer/aykırıya toleranslı.
✅ Paralelleşir (hızlı eğitim).

❌ Gradient boosting kadar keskin doğruluk vermez (genelde).
❌ Büyük modeller hafıza yer, tahmin yavaşlayabilir.
❌ Ekstrapolasyon yapamaz (eğitim aralığı dışını öğrenemez — tüm ağaçlarda ortak).
❌ Tek ağaç kadar yorumlanır değil ("gri kutu").

---

## 6. Diğer bagging türevleri

- **Extra Trees (Extremely Randomized):** Bölme eşiklerini de rastgele seçer →
  daha hızlı, daha çok çeşitlilik.
- **Isolation Forest:** Anomali/aykırı değer tespiti için (denetimsiz). Nadir
  noktaları "izole etmek kolay" mantığı. Dolandırıcılık tespitinde popüler.

---

## 7. Ne zaman ağaç tabanlı?

- **Tablo (tabular) verisi:** Ağaçlar burada hâlâ şampiyon (2026'da bile derin
  öğrenmeyi çoğu tablo görevinde yenerler — Modül 15).
- **Doğrusal olmayan, etkileşimli ilişkiler.**
- **Karışık tip özellikler** (sayısal + kategorik).
- Hızlı, sağlam taban çizgisi istiyorsan: Random Forest.
- Son birkaç puan doğruluk istiyorsan: → **Gradient Boosting (Modül 10).**

---

## 🎯 Alıştırma

1. BTC verisinde tek bir derin karar ağacı eğit. Eğitim doğruluğu ~%100, test
   doğruluğu düşük olacak — overfit'i gör. Sonra `max_depth=3` ile karşılaştır.
2. Random Forest kur, OOB skorunu test skoruyla karşılaştır (yakın olmalı).
3. Permütasyon önemiyle en etkili 5 göstergeyi bul. Varsayılan impurity önemiyle
   sırası farklı mı? Neden?

---

## ✅ Kontrol listesi

- [ ] Karar ağacının nasıl böldüğünü (Gini/entropi) biliyorum.
- [ ] Tek ağacın neden overfit ettiğini ve çözümlerini biliyorum.
- [ ] Bagging (varyans↓) ile boosting (bias↓) farkını biliyorum.
- [ ] Random Forest'taki "rastgele özellik alt kümesi" hilesini anlıyorum.
- [ ] Permütasyon öneminin neden varsayılandan güvenilir olduğunu biliyorum.

Sonraki → [Modül 10: Gradient Boosting (XGBoost, LightGBM, CatBoost)](10-gradient-boosting.md)
