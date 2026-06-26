# Modül 03 — Olasılık Dağılımları

> **Hedef:** Gerçek dünyadaki belirsizliği kalıplaşmış "dağılım"larla
> modellemek. Doğru dağılımı seçmek, doğru modeli seçmenin yarısıdır.

Bir dağılım, bir rastgele değişkenin hangi değeri hangi olasılıkla aldığını
söyleyen "reçete"dir. Birkaç parametreyle (örn. ortalama, std) tüm davranışı
özetler.

---

## 1. Kesikli dağılımlar

### Bernoulli — tek deneme, iki sonuç
Bir kez yazı-tura: başarı olasılığı p. X ∈ {0, 1}.
- E[X] = p, Var = p(1−p).
- Kullanım: "yarın yükselir mi?" (1/0), tıklama/tık-yok.

### Binom — n bağımsız Bernoulli denemesi
n denemede kaç başarı? Örn. 10 işlemden kaçı kârlı?
$$P(X=k) = \binom{n}{k} p^k (1-p)^{n-k}$$
- E[X] = np, Var = np(1−p).

```python
from scipy import stats
# %55 kazanma oranıyla 20 işlemden en az 13'ünün kârlı olma olasılığı
print(1 - stats.binom.cdf(12, n=20, p=0.55))
```

### Poisson — sabit aralıkta nadir olay sayısı
Birim zamanda ortalama λ olay olurken kaç tane gerçekleşir? Örn. saatte gelen
müşteri, günde tetiklenen sinyal, sunucuya gelen istek.
$$P(X=k) = \frac{\lambda^k e^{-\lambda}}{k!}$$
- E[X] = Var = λ (ortalama = varyans; bu eşitlik bozulursa "overdispersion",
  Modül 06'da negatif binom kullanırız).

### Geometrik / Negatif Binom
İlk başarıya kadar kaç deneme? ("Kaç işlemde bir büyük kazanç gelir?")

---

## 2. Sürekli dağılımlar

### Normal (Gauss) — istatistiğin kralı
Çan eğrisi. İki parametre: ortalama μ, std σ.
$$f(x) = \frac{1}{\sigma\sqrt{2\pi}} e^{-\frac{(x-\mu)^2}{2\sigma^2}}$$

**68-95-99.7 kuralı:** Verinin ~%68'i μ±1σ, ~%95'i μ±2σ, ~%99.7'si μ±3σ içinde.

```python
from scipy import stats
# Getiri ~ N(0.1, 2.5). -%5'ten kötü gün olasılığı?
print(stats.norm.cdf(-5, loc=0.1, scale=2.5))   # ~%2
```

> ⚠️ **Finansta büyük tuzak:** Getiriler **tam normal değildir** — şişman
> kuyrukludur (kurtosis yüksek). "5-sigma" olaylar normalde 3.5 milyon yılda
> bir olmalı ama piyasalarda yılda birkaç kez olur. Risk modellerinde Student-t
> kullan.

### Standart Normal (Z) ve standartlaştırma
Herhangi bir normalı μ=0, σ=1 hâline getirme:
$$z = \frac{x - \mu}{\sigma}$$
Z-skoru "kaç standart sapma uzakta?" sorusunu yanıtlar. Karşılaştırma ve
aykırı değer tespitinde temel araç.

### Üstel (exponential) — olaylar arası bekleme süresi
Poisson olaylarının arasındaki süre. "Bir sonraki sinyale kaç dakika?"
"Belleksiz" (memoryless) özelliği vardır.

### Üniform — her değer eşit olası
[a, b] aralığında düz. Simülasyon ve rastgele örnekleme temeli.

### Student-t — kalın kuyruklu normal
Normale benzer ama kuyrukları kalın. **Küçük örneklemlerde** ve **finansal
getirilerde** normal yerine kullanılır. Serbestlik derecesi (df) arttıkça
normale yakınsar.

### Log-normal — çarpık, pozitif değerler
Logaritması normal olan değişken. Fiyatlar, gelir, dosya boyutu — pozitif ve
sağa çarpık her şey. (Fiyat log-normal ise, log-getiri normaldir.)

### Diğer önemli olanlar
- **Ki-kare (χ²):** Varyans testleri, bağımsızlık testi (Modül 04).
- **F dağılımı:** İki varyansın oranı, ANOVA ve regresyon testi.
- **Beta:** [0,1] aralığında; oranlar/olasılıklar için. Bayesian'da prior olarak
  ideal (Modül 11).
- **Gamma:** Pozitif çarpık; bekleme süreleri, sigorta hasarları.

---

## 3. Merkezi Limit Teoremi (CLT) — istatistiğin sihri

> **Çok sayıda bağımsız rastgele değişkenin ortalaması (veya toplamı),
> bireysel dağılımları ne olursa olsun, yaklaşık NORMAL dağılır.**

Bu yüzden normal dağılım her yerde karşımıza çıkar ve bu yüzden örneklem
ortalaması hakkında çıkarım yapabiliriz (Modül 04'ün temeli).

```python
import numpy as np
import matplotlib.pyplot as plt
rng = np.random.default_rng(0)

# Hiç normal olmayan bir dağılımdan (üstel) örnek alalım
orneklem_ortalamalari = [rng.exponential(scale=2, size=30).mean()
                         for _ in range(10000)]
plt.hist(orneklem_ortalamalari, bins=50)  # çan eğrisine benzeyecek!
plt.title("CLT: üstel dağılımdan alınan ortalamalar normale döner")
plt.savefig("clt.png")
```

> 🔑 n ≥ 30 genelde "yeterli" kabul edilir (çok çarpık dağılımlarda daha fazla).

---

## 4. Hangi dağılımı seçmeli? (karar rehberi)

| Veri / Soru | Dağılım |
|---|---|
| Evet/Hayır, tek deneme | Bernoulli |
| n denemede başarı sayısı | Binom |
| Sabit aralıkta nadir olay sayısı | Poisson |
| Sürekli, simetrik, doğal | Normal |
| Sürekli, simetrik, kalın kuyruk / küçük örneklem | Student-t |
| Pozitif, sağa çarpık (fiyat, gelir) | Log-normal / Gamma |
| Olaylar arası süre | Üstel |
| Oran / olasılık (0–1 arası) | Beta |

---

## 5. Dağılım uydurma (fitting)

Elindeki veriye hangi dağılım uyuyor?

```python
from scipy import stats
veri = ...  # senin getirilerin

# Normal mi t mi daha iyi uyuyor? Parametreleri tahmin et
mu, sigma = stats.norm.fit(veri)
df, loc, scale = stats.t.fit(veri)

# Görsel: QQ-plot — noktalar doğru üzerindeyse o dağılıma uyar
stats.probplot(veri, dist="norm", plot=plt)
# Sapma kuyruklardaysa → şişman kuyruk → t dene
```

QQ-plot (kantil-kantil grafiği) dağılım uyumunu görselden anlamanın en hızlı
yoludur. Kuyruklarda "S" şekli görürsen normal varsayımın çöküyor demektir.

---

## 🎯 Alıştırma

1. BTC günlük log-getirilerine normal ve Student-t dağılımı uydur. QQ-plot çiz.
   Hangisi kuyrukları daha iyi yakalıyor?
2. Bir stratejinin günde ortalama 3 sinyal ürettiğini varsay (Poisson, λ=3).
   Bir günde 0 sinyal gelme olasılığı nedir? 6+ sinyal?
3. CLT simülasyonunu kendi yaz: üniform dağılımdan n=2, 5, 30 için ortalama
   dağılımlarını çiz. n büyüdükçe çan eğrisine yaklaşmayı gözlemle.

---

## ✅ Kontrol listesi

- [ ] Kesikli ve sürekli dağılımları ayırt ediyorum (PMF vs PDF).
- [ ] Normal dağılımın finansta neden yetersiz kaldığını biliyorum.
- [ ] CLT'nin neden tüm çıkarımsal istatistiğin temeli olduğunu anlıyorum.
- [ ] Bir veriye bakıp uygun dağılımı tahmin edebiliyorum.

Sonraki → [Modül 04: Çıkarımsal İstatistik](04-cikarimsal-istatistik.md)
