# Modül 01 — Betimsel İstatistik

> **Hedef:** Bir veri yığınına bakıp "burada ne oluyor?" sorusuna sayılarla
> ve grafiklerle cevap verebilmek.

İstatistik iki ana dala ayrılır:
- **Betimsel (descriptive):** Elindeki veriyi *özetler*. "Müşterilerin yaş
  ortalaması 34."
- **Çıkarımsal (inferential):** Örneklemden *tüm evrene* dair sonuç çıkarır
  (Modül 04). "Türkiye'deki tüm müşterilerin yaş ortalaması %95 ihtimalle 33–35."

Bu modül birincisidir — her şeyin temeli.

---

## 1. Veri tipleri

Yöntem seçimi veri tipine bağlıdır. Yanlış tip → yanlış analiz.

| Tip | Açıklama | Örnek |
|---|---|---|
| **Nicel — sürekli** | Ölçülen, ondalıklı olabilir | Boy, fiyat, sıcaklık |
| **Nicel — kesikli** | Sayılan tam sayı | Çocuk sayısı, işlem adedi |
| **Kategorik — nominal** | Sırasız etiket | Renk, şehir, parite |
| **Kategorik — sıralı (ordinal)** | Sıralı etiket | Az/Orta/Çok, A/B/C notu |

---

## 2. Merkezi eğilim ölçüleri — "tipik değer nedir?"

- **Ortalama (mean):** Tüm değerlerin toplamı / adet.
  $$\bar{x} = \frac{1}{n}\sum_{i=1}^{n} x_i$$
  Aykırı değerlere (outlier) **çok duyarlıdır**.

- **Medyan:** Sıralandığında tam ortadaki değer. Aykırı değerlere **dayanıklı**.
  Maaş, ev fiyatı gibi çarpık dağılımlarda ortalamadan iyidir.

- **Mod:** En sık tekrar eden değer. Kategorik veride tek seçenektir.

> 🔑 **Sezgi:** Bir mahalledeki 9 kişi 30.000 TL, 1 kişi 10 milyon TL
> kazanıyorsa **ortalama** ~1 milyon (yanıltıcı!), **medyan** 30.000 (gerçekçi).
> Çarpık veride medyana güven.

---

## 3. Dağılım/yayılım ölçüleri — "değerler ne kadar saçılmış?"

- **Aralık (range):** max − min. Basit ama aykırı değere çok duyarlı.

- **Varyans:** Ortalamadan sapmaların karelerinin ortalaması.
  $$s^2 = \frac{1}{n-1}\sum_{i=1}^{n}(x_i - \bar{x})^2$$
  > Neden `n-1`? **Bessel düzeltmesi** — örneklemden evren varyansını tahmin
  > ederken yanlılığı giderir. Tüm evren elindeyse `n` kullanılır.

- **Standart sapma (std):** Varyansın karekökü. Verinin **kendi biriminde**
  olduğu için yorumlaması kolaydır (varyans "kare birim"dedir).

- **IQR (çeyrekler arası açıklık):** Q3 − Q1 (yani %75'lik − %25'lik dilim).
  Aykırı değere dayanıklı yayılım ölçüsü. Boxplot'un kutusu budur.

- **Değişim katsayısı (CV):** std / ortalama. Birimsiz; farklı ölçekleri
  karşılaştırmak için (örn. BTC'nin mi altının mı oynaklığı yüksek?).

---

## 4. Dağılımın şekli

- **Çarpıklık (skewness):** Asimetri. Sağa çarpık (kuyruğu sağda) →
  ortalama > medyan. Gelir, kripto getirileri genelde sağa çarpıktır.
- **Basıklık (kurtosis):** Kuyrukların kalınlığı. Yüksek kurtosis = "şişman
  kuyruk" = aşırı olaylar (kriz, pump) beklenenden sık. Finansta kritik.

---

## 5. İki değişken arası ilişki

- **Kovaryans:** İki değişkenin birlikte nasıl değiştiği. İşareti yönü verir
  ama büyüklüğü ölçeğe bağlı, yorumlaması zor.

- **Korelasyon (Pearson r):** Kovaryansın standartlaştırılmış hâli, **−1 ile +1**
  arası. Doğrusal ilişkinin gücü.
  $$r = \frac{\text{cov}(x,y)}{s_x \, s_y}$$

> ⚠️ **En önemli uyarı:** **Korelasyon nedensellik değildir.** Dondurma
> satışı ile boğulma vakaları korelelidir — ortak sebep *yaz sıcağı*. Bunu
> Modül 13'te (nedensellik) çözeceğiz.

- **Spearman korelasyonu:** Doğrusal olmayan ama **monoton** (hep artan/azalan)
  ilişkileri yakalar. Sıralamalar üzerinden hesaplanır, aykırı değere dayanıklı.

---

## 6. Görselleştirme — "bir grafik bin sayıya bedeldir"

| Grafik | Ne gösterir |
|---|---|
| **Histogram** | Tek değişkenin dağılımı (şekli, çarpıklığı) |
| **Boxplot** | Medyan, IQR, aykırı değerler; grupları karşılaştırma |
| **Scatter (saçılım)** | İki değişken arası ilişki |
| **Violin** | Histogram + boxplot karışımı (dağılım yoğunluğu) |
| **Heatmap** | Korelasyon matrisi |

> 📊 **Anscombe Dörtlüsü:** Aynı ortalama, varyans ve korelasyona sahip 4
> veri seti tamamen farklı görünür. **Daima önce grafiğe bak**, sonra sayıya.

---

## 7. Python ile uçtan uca

```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Örnek: BTC günlük getirileri (yüzde)
rng = np.random.default_rng(42)
getiriler = rng.normal(loc=0.1, scale=2.5, size=300)  # ~%0.1 ort, %2.5 std

s = pd.Series(getiriler, name="gunluk_getiri_%")

# Tek satırda özet
print(s.describe())
# count, mean, std, min, 25%, 50% (medyan), 75%, max

# Dayanıklı ölçüler
print("Medyan :", s.median())
print("IQR    :", s.quantile(0.75) - s.quantile(0.25))
print("Çarpıklık:", s.skew())
print("Basıklık :", s.kurtosis())   # fazla pozitifse şişman kuyruk

# Görselleştirme
fig, ax = plt.subplots(1, 2, figsize=(11, 4))
sns.histplot(s, kde=True, ax=ax[0]); ax[0].set_title("Dağılım")
sns.boxplot(x=s, ax=ax[1]);          ax[1].set_title("Boxplot + aykırı")
plt.tight_layout(); plt.savefig("ozet.png")

# İki değişken korelasyonu
df = pd.DataFrame({"getiri": getiriler, "hacim": rng.normal(100, 20, 300)})
print("Pearson :", df.corr().iloc[0, 1])
print("Spearman:", df.corr(method="spearman").iloc[0, 1])
```

---

## 8. Aykırı değer tespiti (hızlı yöntem)

```python
# IQR kuralı: Q1 - 1.5*IQR altı veya Q3 + 1.5*IQR üstü aykırıdır
Q1, Q3 = s.quantile(0.25), s.quantile(0.75)
IQR = Q3 - Q1
aykiri = s[(s < Q1 - 1.5*IQR) | (s > Q3 + 1.5*IQR)]
print(f"{len(aykiri)} aykırı değer bulundu")
```

Aykırı değeri **silmek her zaman doğru değil** — bazen en değerli bilgi odur
(dolandırıcılık, kriz, fırsat). Önce *neden* aykırı olduğunu sor.

---

## 🎯 Alıştırma

1. Bu repodaki BTC botunun `src/exchange.py` ile çektiği 300 günlük kapanış
   fiyatlarını al. Günlük getiriyi hesapla (`pct_change`).
2. Ortalama, medyan, std, IQR, çarpıklık ve basıklığı yazdır. Getiriler
   simetrik mi, şişman kuyruklu mu?
3. Histogram + boxplot çiz. Kaç aykırı gün var? O günlerde piyasada ne olmuş?

---

## ✅ Kontrol listesi

- [ ] Ortalama ile medyanın ne zaman ayrıştığını biliyorum.
- [ ] Std ile IQR arasındaki dayanıklılık farkını anlıyorum.
- [ ] Korelasyonun nedensellik olmadığını içselleştirdim.
- [ ] Bir veri setini gördüğümde önce histogram/boxplot çiziyorum.

Sonraki → [Modül 02: Olasılık Teorisi](02-olasilik-teorisi.md)
