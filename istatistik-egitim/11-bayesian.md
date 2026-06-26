# Modül 11 — Bayesian İstatistik

> **Hedef:** Belirsizliği "tek sayı" yerine **olasılık dağılımı** olarak ifade
> etmek. Az veriyle, ön bilgiyi (prior) kullanarak ve belirsizliği dürüstçe
> raporlayarak çıkarım yapmak. Modül 02'deki Bayes kuralının tam çiçeklenmesi.

---

## 1. İki felsefe: Frekansçı vs Bayesian

| | Frekansçı (Modül 04) | Bayesian |
|---|---|---|
| Parametre (μ) | Sabit, bilinmeyen | **Rastgele değişken** (inanç) |
| Olasılık ne demek? | Uzun vadeli sıklık | İnanç derecesi |
| Sonuç | Nokta tahmin + p-değeri | **Posterior dağılım** |
| Ön bilgi | Kullanılmaz | **Prior** ile katılır |
| Belirsizlik | Güven aralığı (yorumu zor) | Credible interval (doğrudan yorum) |

> **Bayesian'ın güzelliği:** "Parametrenin %95 ihtimalle [a, b] arasında olduğunu"
> *gerçekten* söyleyebilirsin (frekansçı CI bunu söyleyemez, Modül 04).

---

## 2. Bayes kuralı, parametreler için

$$\underbrace{P(\theta \mid \text{veri})}_{\text{posterior}} \propto
\underbrace{P(\text{veri} \mid \theta)}_{\text{likelihood}} \times
\underbrace{P(\theta)}_{\text{prior}}$$

- **Prior P(θ):** Veriyi görmeden önceki inancın. "Stratejinin kazanma oranı
  muhtemelen %45–55 arası."
- **Likelihood:** Veri, θ'ya göre ne kadar olası.
- **Posterior:** Güncellenmiş inanç. **Tüm cevap budur** — bir dağılım.

> 🔑 **Öğrenme = inanç güncelleme.** Az veri → posterior prior'a yakın. Çok veri
> → veri prior'ı ezer (likelihood baskın). Veri biriktikçe doğruya yakınsarsın.

---

## 3. Konjuge örnek (elle hesaplanan sezgi): Beta-Binom

Bir stratejinin kazanma oranını (p) tahmin edelim.
- **Prior:** Beta(α, β). Beta(2,2) = "muhtemelen %50 civarı, ama emin değilim."
- **Veri:** n işlemden k kazanç (Binom likelihood).
- **Posterior:** Beta(α+k, β+n−k). **Sihir:** aynı aileden çıkar (konjuge).

```python
from scipy import stats
import numpy as np
import matplotlib.pyplot as plt

alpha0, beta0 = 2, 2          # zayıf prior: %50 civarı
kazanc, kayip = 14, 6         # 20 işlemde 14 kazanç

post = stats.beta(alpha0 + kazanc, beta0 + kayip)
x = np.linspace(0, 1, 200)
plt.plot(x, post.pdf(x))
print(f"Posterior ortalama kazanma oranı: {post.mean():.3f}")
print(f"%95 credible interval: [{post.ppf(0.025):.3f}, {post.ppf(0.975):.3f}]")
print(f"Kazanma oranı > 0.5 olma olasılığı: {1 - post.cdf(0.5):.3f}")
```

Son satır frekansçının ASLA söyleyemeyeceği bir cümle: "Stratejinin gerçekten
kârlı (p>0.5) olma olasılığı %X." Karar verme için bundan değerlisi yok.

---

## 4. Prior seçimi — güç ve sorumluluk

- **Bilgilendirici (informative):** Güçlü alan bilgisi varsa. Az veriyi telafi eder.
- **Zayıf bilgilendirici (weakly informative):** Mantıklı sınırlar koyar, veriyi
  serbest bırakır. **Modern pratikte önerilen varsayılan.**
- **Belirsiz (flat/uninformative):** "Hiçbir fikrim yok." Dikkat: bazen istemeden
  saçma sonuç verir.

> ⚠️ Prior öznel diye eleştirilir — ama **her analizde varsayım vardır**;
> Bayesian onları açıkça yazar. **Duyarlılık analizi** yap: farklı prior'larla
> sonuç çok değişiyorsa, verin yetersiz demektir (bu da bilgidir).

---

## 5. Gerçek modeller: MCMC ve olasılıksal programlama

Çoğu gerçek modelde posterior'ın kapalı formülü yoktur. Çözüm: **örnekleme**.
**MCMC** (Markov Chain Monte Carlo) posterior'dan binlerce örnek çeker:
- **Metropolis-Hastings:** Klasik, basit.
- **Hamiltonian Monte Carlo (HMC) / NUTS:** Modern, verimli (PyMC, Stan kullanır).
- **Variational Inference (VI):** MCMC'den hızlı, yaklaşık; büyük veride.

### PyMC ile Bayesian lineer regresyon
```python
import pymc as pm
import numpy as np

with pm.Model() as model:
    # Prior'lar (katsayılara dair önsel inanç)
    alpha = pm.Normal("alpha", mu=0, sigma=10)
    beta  = pm.Normal("beta",  mu=0, sigma=10, shape=X.shape[1])
    sigma = pm.HalfNormal("sigma", sigma=1)

    # Beklenen değer
    mu = alpha + pm.math.dot(X, beta)

    # Likelihood (gözlenen veri)
    y_obs = pm.Normal("y_obs", mu=mu, sigma=sigma, observed=y)

    # Posterior'dan örnekle (NUTS)
    idata = pm.sample(2000, tune=1000, chains=4, target_accept=0.9)

import arviz as az
print(az.summary(idata, var_names=["alpha", "beta", "sigma"]))
az.plot_trace(idata)   # zincir yakınsadı mı? (trace düz "tüylü tırtıl" olmalı)
```

### Yakınsama kontrolü (şart!)
- **R-hat (R̂):** < 1.01 olmalı (zincirler aynı yere yakınsadı mı?).
- **ESS (effective sample size):** Yeterince yüksek mi?
- **Trace plot:** "Tüylü tırtıl" gibi düz olmalı; trend/takılma kötüdür.
- **Divergences:** Varsa `target_accept` artır veya modeli yeniden parametrele.

---

## 6. Hiyerarşik (çok seviyeli) modeller — Bayesian'ın süper gücü

Gruplar arası bilgi paylaşımı. Örn. her parite için ayrı strateji parametresi
ama hepsi ortak bir "havuzdan" gelir:
- **Tam havuzlama (pooling):** Tüm pariteler aynı (grupları yok sayar).
- **Havuzlama yok:** Her parite tamamen ayrı (az veride gürültülü).
- **Kısmi havuzlama (hiyerarşik):** İkisinin akıllı ortası — az verili gruplar
  havuza doğru "shrink" olur (regularizasyonun Bayesian hâli). **En iyisi.**

> Bu, "küçük örneklemli gruplar" probleminin (az işlemli bir parite) zarif çözümü.

---

## 7. Bayesian'ın güçlü olduğu yerler

- **Az veri:** Prior boşluğu doldurur (yeni strateji, nadir olay).
- **Belirsizlik kritik:** Risk/pozisyon büyüklüğü kararları (sadece tahmin
  değil, ne kadar emin olduğun da önemli).
- **Karar teorisi:** Posterior'ı beklenen fayda hesabıyla birleştirip optimal
  karar (Kelly kriteri, optimal bahis boyutu).
- **A/B testi:** "B'nin A'dan iyi olma olasılığı %92" — yöneticiye p-değerinden
  çok daha anlaşılır.
- **Bayesian optimizasyon:** Hiperparametre/strateji ayarını akıllıca arar
  (Optuna'nın altındaki fikir).

### Dezavantajları
- Hesaplama pahalı (MCMC yavaş olabilir).
- Prior ve model kurmak uzmanlık ister.
- Çok büyük veride genelde boosting daha pratik (ham tahmin doğruluğu için).

---

## 🎯 Alıştırma

1. Stratejinin kazanma oranını Beta-Binom ile modelle. 10, 50, 200 işlemle
   posterior nasıl daralıyor (belirsizlik azalıyor)? "p>0.5 olasılığını" yazdır.
2. PyMC ile Bayesian lineer regresyon kur (getiriyi göstergelerle). Katsayıların
   credible interval'larına bak — hangileri güvenle 0'dan farklı?
3. İki strateji için hiyerarşik model kur. Az işlemli stratejinin tahmini, çok
   işlemlinin ortalamasına doğru ne kadar "shrink" oldu?

---

## ✅ Kontrol listesi

- [ ] Frekansçı ve Bayesian felsefe farkını açıklayabiliyorum.
- [ ] Prior → likelihood → posterior akışını biliyorum.
- [ ] Credible interval'ı doğru (doğrudan olasılık olarak) yorumluyorum.
- [ ] MCMC'nin neden gerektiğini ve yakınsama kontrolünü biliyorum.
- [ ] Hiyerarşik modelin kısmi havuzlama avantajını anlıyorum.

Sonraki → [Modül 12: Zaman Serisi](12-zaman-serisi.md)
