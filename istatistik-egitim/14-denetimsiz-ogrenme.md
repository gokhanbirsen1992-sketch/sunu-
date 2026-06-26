# Modül 14 — Denetimsiz Öğrenme

> **Hedef:** Etiketsiz veride (y yok) yapı keşfetmek: gruplama (kümeleme),
> boyut indirgeme ve anomali tespiti. "Verim ne anlatıyor?" sorusunu sorar.

---

## 1. Denetimli vs denetimsiz

- **Denetimli (Modül 05-13):** Girdi X + bilinen hedef y. "Tahmin et."
- **Denetimsiz:** Sadece X. "Yapıyı bul, grupla, sıkıştır, anomali yakala."

Kullanım: müşteri segmentasyonu, piyasa rejimi tespiti, gürültü azaltma,
görselleştirme, dolandırıcılık/anomali tespiti, özellik üretimi.

---

## 2. Boyut indirgeme

Çok özellikli veriyi az boyuta sıkıştırmak — görselleştirme, gürültü azaltma,
"boyut laneti"yle (curse of dimensionality) mücadele.

### PCA (Temel Bileşen Analizi) — doğrusal
Verideki **en çok varyansı** taşıyan yeni eksenleri (temel bileşenler) bulur.
İlk birkaç bileşen genelde bilginin çoğunu taşır.

```python
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

Xs = StandardScaler().fit_transform(X)     # PCA ölçeğe duyarlı → şart
pca = PCA(n_components=0.95)                # varyansın %95'ini tutacak kadar bileşen
X_pca = pca.fit_transform(Xs)
print("Bileşen sayısı:", pca.n_components_)
print("Açıklanan varyans:", pca.explained_variance_ratio_.cumsum())
```

> Kullanım: korele teknik göstergeleri birkaç "faktöre" indirgemek, multicollinearity
> çözmek, görselleştirme. Finansta faktör modellerinin (Fama-French) akrabası.

### t-SNE ve UMAP — doğrusal olmayan, görselleştirme için
Yüksek boyutlu veriyi 2-3 boyuta indirip **kümeleri görsel** olarak ortaya çıkarır.
- **t-SNE:** Güzel kümeler ama yavaş, global yapıyı korumaz.
- **UMAP:** Daha hızlı, global yapıyı daha iyi korur, modern tercih.

> ⚠️ t-SNE/UMAP **sadece görselleştirme** içindir. Eksenler anlamsızdır,
> mesafeler/küme boyutları güvenilir değildir — üzerinde modelleme yapma.

---

## 3. Kümeleme (Clustering)

Benzer gözlemleri gruplama.

### K-Means — en yaygın
Veriyi k kümeye böler; her küme merkezine (centroid) en yakın noktalar.
- k'yı önceden seçmelisin (**Elbow** veya **Silhouette** skoru ile bul).
- Küresel, eşit boyutlu kümeleri varsayar; ölçeğe duyarlı (standartlaştır).

```python
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

for k in range(2, 8):
    km = KMeans(n_clusters=k, n_init=10, random_state=0).fit(Xs)
    print(f"k={k}: silhouette={silhouette_score(Xs, km.labels_):.3f}")
```

### Hiyerarşik kümeleme
Ağaç (dendrogram) oluşturur; k'yı sonradan seçebilirsin. Küçük veride yorumlanabilir.

### DBSCAN — yoğunluk tabanlı
Yoğun bölgeleri küme yapar, seyrek noktaları **gürültü/anomali** işaretler.
- k seçmene gerek yok; **keyfi şekilli** kümeler bulur.
- Aykırı değerlere dayanıklı; anomali tespitinde faydalı.

### GMM (Gaussian Mixture) — olasılıksal kümeleme
Her noktayı kümelere **olasılıkla** atar (yumuşak). K-means'in esnek hâli;
elips şekilli kümeler. Olasılıksal çerçeve (Modül 11 ile bağ).

---

## 4. Anomali / aykırı değer tespiti

Etiketsiz "normalden sapan" gözlemleri bulma (dolandırıcılık, arıza, piyasa şoku).
- **Isolation Forest:** Anomalileri "izole etmek kolaydır" mantığı (Modül 09).
- **Local Outlier Factor (LOF):** Yerel yoğunluk kıyası.
- **One-Class SVM:** "Normal"in sınırını öğrenir.
- **Otoenkoder (DL):** Yeniden yapılandırma hatası yüksek olanlar anomali.

```python
from sklearn.ensemble import IsolationForest
iso = IsolationForest(contamination=0.02, random_state=0).fit(X)
anomali = iso.predict(X) == -1     # -1: anomali
```

---

## 5. İlişki/birliktelik kuralları

"X alanlar Y de alır" (market basket). Apriori, FP-Growth algoritmaları.
Öneri sistemleri ve çapraz satışta kullanılır.

---

## 6. Değerlendirme — etiketsiz zorluğu

Denetimsizde "doğru cevap" yok, değerlendirme zor:
- **Silhouette, Davies-Bouldin, Calinski-Harabasz:** İç tutarlılık ölçüleri.
- **İş anlamı:** Kümeler/segmentler **yorumlanabilir ve eyleme dönük** mü?
  En önemli test budur. "İstatistiksel olarak güzel ama anlamsız" kümeden kaçın.
- **Kararlılık:** Veriyi biraz değiştirince kümeler tutarlı mı?

---

## 7. Trading/finans uygulamaları

- **Piyasa rejimi tespiti:** Getiri/oynaklık özellikleriyle kümeleme →
  "boğa / ayı / yatay / kriz" rejimleri. Rejime göre strateji değiştir.
- **Varlık kümeleme:** Benzer davranan varlıkları grupla (portföy çeşitlendirme).
- **PCA faktörleri:** Çok sayıda göstergeden ortak faktörler çıkar.
- **Anomali:** Olağandışı fiyat/hacim hareketlerini yakala.

---

## 🎯 Alıştırma

1. BTC günlük verisinden özellikler üret (getiri, oynaklık, hacim, RSI).
   Standartlaştırıp K-Means uygula. Silhouette ile en iyi k'yı bul. Kümeler
   piyasa rejimlerine (sakin/çalkantılı) karşılık geliyor mu?
2. Aynı veriyi UMAP ile 2B'ye indir, kümeleri renklendirip görselleştir.
3. Isolation Forest ile anormal günleri bul. Bu günlerde gerçekte ne olmuş?
   (Haber/kriz ile eşleşiyor mu?)

---

## ✅ Kontrol listesi

- [ ] Denetimli/denetimsiz farkını biliyorum.
- [ ] PCA'nın ne yaptığını (varyans ekseni) ve ölçekleme gereğini biliyorum.
- [ ] t-SNE/UMAP'ın sadece görselleştirme için olduğunu biliyorum.
- [ ] K-Means, DBSCAN, GMM'nin farklarını ve ne zaman kullanılacağını biliyorum.
- [ ] Anomali tespiti yöntemlerinden en az ikisini biliyorum.
- [ ] Küme kalitesini iş anlamıyla değerlendirmeyi biliyorum.

Sonraki → [Modül 15: Modern & 2026 Yöntemleri](15-modern-2026.md)
