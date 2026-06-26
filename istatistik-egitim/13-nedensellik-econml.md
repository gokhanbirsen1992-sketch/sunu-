# Modül 13 — Nedensellik ve EconML

> **Hedef:** "Korelasyon nedensellik değildir"in ötesine geçmek. **Bir şeyin
> bir şeye gerçekten SEBEP olup olmadığını** ve etkisinin **kime ne kadar**
> olduğunu ölçmek. Senin sorduğun **EconML** (Microsoft'un nedensel ML
> kütüphanesi) burada.

> 📌 Tahmin (prediction) ≠ nedensellik (causation). ML modelleri "ne olacak"
> tahmin eder; nedensellik "müdahale edersem ne değişir" sorusunu yanıtlar.
> Karar vermek (fiyat değiştir, ilaç ver, kampanya yap) ikincisini gerektirir.

---

## 1. Temel problem: karşı-olgu (counterfactual)

Bir kişiye reklam gösterdin, satın aldı. **Reklam mı sebep oldu, yoksa zaten
alacak mıydı?** Aynı kişinin "reklam görmemiş hâlini" asla göremezsin — bu
**nedensel çıkarımın temel problemi**dir.

- **Tedavi (treatment, T):** Müdahale (reklam, ilaç, fiyat indirimi).
- **Sonuç (outcome, Y):** Ölçtüğümüz (satın alma, iyileşme, getiri).
- **ATE (Ortalama Tedavi Etkisi):** E[Y(tedavi) − Y(tedavisiz)] tüm popülasyonda.
- **CATE (Koşullu/bireysel etki):** Etki kişiden kişiye değişir — "kime işe yarar?"

---

## 2. Confounding (karıştırıcı) — neden basit korelasyon yanıltır

**Confounder:** Hem tedaviyi hem sonucu etkileyen ortak sebep.

> Örnek: "Premium kullanıcılar daha çok harcıyor" → Premium harcamaya mı sebep,
> yoksa zaten zengin/bağlı kullanıcılar mı premium alıyor? **Gelir/bağlılık**
> burada confounder. Düzeltmezsen etkiyi abartırsın.

**Pearl'in nedensellik merdiveni:**
1. **İlişki (görme):** P(Y|X) — sıradan ML.
2. **Müdahale (yapma):** P(Y | do(T)) — "T'yi zorlarsam?"
3. **Karşı-olgu (hayal etme):** "Keşke T farklı olsaydı?"

**Yönlü graf (DAG):** Değişkenler arası nedensel okları çiz; hangi değişkenleri
kontrol edeceğini (ve hangilerini **kontrol ETMEMEN** gerektiğini — collider
bias!) bu belirler.

---

## 3. Altın standart: Randomize Deney (RCT / A/B test)

Tedaviyi **rastgele** atarsan, confounder otomatik dengelenir → fark gerçek
nedensel etkidir. Mümkünse her zaman bunu yap (A/B test).

Ama çoğu zaman deney yapamazsın (etik, maliyet, geçmiş veri). O zaman
**gözlemsel veriden** nedensellik çıkarman gerekir → aşağıdaki yöntemler.

---

## 4. Gözlemsel nedensellik yöntemleri

### a) Eğilim Skoru (Propensity Score) ve Eşleştirme
"Tedavi alma olasılığı"nı (confounder'lardan) modelle, sonra benzer eğilimli
tedavili/tedavisiz birimleri eşleştir veya ağırlıklandır (IPW).

### b) Araç Değişken (Instrumental Variable, IV)
Tedaviyi etkileyen ama sonucu **sadece tedavi yoluyla** etkileyen bir değişken
bul (örn. rastgele atanmış bir teşvik). Gizli confounder olsa bile etkiyi
kurtarır. 2SLS (iki aşamalı en küçük kareler).

### c) Fark-İçinde-Fark (Difference-in-Differences, DiD)
Bir grup tedavi alır, biri almaz; ikisinin **değişimini** karşılaştır. Politika
değerlendirmesinin klasiği ("paralel trend" varsayımıyla).

### d) Regresyon Süreksizliği (RDD)
Bir eşiğin (örn. sınav notu, gelir sınırı) hemen iki yanını karşılaştır.

### e) Synthetic Control
Tedavi görmeyen birimlerden "yapay ikiz" inşa et (tek birimli politika analizi).

---

## 5. EconML — nedensel ML kütüphanesi (Microsoft)

EconML, **makine öğrenmesi gücünü** (boosting, random forest — Modül 9-10)
**nedensel çıkarımla** birleştirir. Özellikle **heterojen etki (CATE)** tahmininde
güçlüdür: "Bu müdahale **kime** ne kadar işe yarar?" Hedefleme/kişiselleştirme
için altın değerinde.

### Double Machine Learning (DML) — EconML'in kalbi
İki ML modeli kurar:
1. Y'yi confounder'lardan tahmin et → artığını al.
2. T'yi confounder'lardan tahmin et → artığını al.
3. **Artıkları regresyonla** → confounder'lardan arındırılmış nedensel etki.

> Bu "ortogonalleştirme" (Neyman) sayesinde, ML modelleri biraz hatalı olsa bile
> nedensel etki tahmini geçerli kalır. Zarif ve güçlü.

```python
from econml.dml import LinearDML
from sklearn.ensemble import GradientBoostingRegressor

# Y: sonuç (örn. müşteri getirisi), T: tedavi (örn. indirim), X/W: özellikler/confounder
est = LinearDML(
    model_y=GradientBoostingRegressor(),   # Y ~ confounder
    model_t=GradientBoostingRegressor(),   # T ~ confounder
    random_state=0,
)
est.fit(Y, T, X=X, W=W)        # X: etki heterojenliği, W: kontrol değişkenleri
print("Ortalama tedavi etkisi (ATE):", est.ate(X))
print("%95 güven aralığı:", est.ate_interval(X))

# Bireysel/koşullu etki (CATE): kime ne kadar etki ediyor?
cate = est.effect(X)           # her birey için tahmini etki
```

### EconML'deki diğer tahminciler
- **CausalForestDML:** Random Forest tabanlı CATE (Athey & Wager). Etki
  heterojenliğini esnek yakalar.
- **DRLearner (Doubly Robust):** Eğilim + sonuç modelini birleştirir; biri
  yanlışsa diğeri kurtarır.
- **Meta-learnerlar (S/T/X-learner):** Herhangi bir ML modelini nedensel etki
  tahminine çevirme şablonları.
- **OrthoIV / DeepIV:** ML ile araç değişken yöntemleri.
- **Politika öğrenme (PolicyTree):** "Kime tedavi vermeliyim?" optimal kuralı.

---

## 6. Uplift Modelleme — pazarlama/CRM uygulaması

"Kampanyayı **kime** göndereyim?" sorusu. 4 müşteri tipi:
- **İkna edilebilir (persuadable):** Sadece kampanya görürse alır → **hedefle!**
- **Kesin alıcı (sure thing):** Zaten alır → kampanya israf.
- **Kayıp dava (lost cause):** Hiç almaz → israf.
- **Uyuyan köpek (sleeping dog):** Kampanya görünce kızar/vazgeçer → **zarar!**

Uplift modelleme (EconML CATE ile yapılır) sadece "ikna edilebilirleri" bulup
bütçeyi verimli kullanır. Klasik "satın alma olasılığı" modeli bunu yapamaz.

---

## 7. Varsayımlar — nedenselliğin ince yazısı

Hiçbir gözlemsel yöntem sihir değildir. Hepsi varsayıma dayanır:
- **Unconfoundedness / ignorability:** Tüm önemli confounder'lar ölçülmüş
  (DML/eşleştirme bunu varsayar — ölçülmeyen confounder varsa sonuç sapar).
- **Overlap/positivity:** Her tip birim hem tedavi hem kontrolde temsil edilmeli.
- **SUTVA:** Bir birimin tedavisi başkasını etkilemez.
- IV için: araç geçerli ve dışlanır (exclusion).

> 🔑 **Duyarlılık analizi** yap: "Ölçülmeyen bir confounder sonucu ne kadar
> değiştirebilirdi?" Nedensel iddia ancak varsayımları kadar güçlüdür. Dürüst ol.

---

## 8. Finans/trading'de nedensellik

- Saf fiyat tahmini çoğunlukla nedensellik gerektirmez (tahmin yeterli).
- Ama **"bu özelliğe göre işlem yaparsam getiri değişir mi?"**, **"şu makro olay
  fiyata SEBEP mi?"**, **"strateji parametresini değiştirmenin gerçek etkisi?"**
  gibi sorular nedenseldir.
- Backtest'teki en büyük yanılgı: korelasyonu nedensellik sanıp canlıda kaybetmek.

---

## 🎯 Alıştırma

1. Sentetik veri üret: bir confounder hem "tedaviyi" hem "sonucu" etkilesin.
   Önce naif korelasyonla etkiyi ölç (yanlış çıkacak), sonra EconML `LinearDML`
   ile confounder'ı kontrol et. Fark ne kadar?
2. `CausalForestDML` ile CATE tahmin et. Etki herkeste aynı mı, yoksa bir alt
   grupta çok mu güçlü? Heterojenliği görselleştir.
3. DAG çiz: bir "collider" ekle ve onu kontrol etmenin sahte ilişki yarattığını
   simülasyonla göster (collider bias).

---

## ✅ Kontrol listesi

- [ ] Tahmin ile nedensellik arasındaki temel farkı biliyorum.
- [ ] Confounding ve karşı-olgu kavramlarını anlıyorum.
- [ ] RCT/A/B testinin neden altın standart olduğunu biliyorum.
- [ ] IV, DiD, eğilim skoru yöntemlerini ne zaman kullanacağımı biliyorum.
- [ ] DML'in (EconML) artık-ortogonalleştirme fikrini anlıyorum.
- [ ] CATE/uplift'in "kime işe yarar" sorusunu çözdüğünü biliyorum.
- [ ] Her nedensel iddianın varsayımlara dayandığını içselleştirdim.

Sonraki → [Modül 14: Denetimsiz Öğrenme](14-denetimsiz-ogrenme.md)
