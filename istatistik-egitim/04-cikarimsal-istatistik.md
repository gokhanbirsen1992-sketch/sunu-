# Modül 04 — Çıkarımsal İstatistik

> **Hedef:** Elimizdeki **örneklemden** (sample), göremediğimiz **evrene**
> (population) dair sonuç çıkarmak ve bu sonuca ne kadar güvenebileceğimizi
> ölçmek. A/B testlerinin, bilimsel makalelerin ve strateji doğrulamasının
> temeli budur.

---

## 1. Örneklem mi evren mi?

- **Evren (population):** İlgilendiğimiz her şey. "Tüm BTC işlemleri."
- **Örneklem (sample):** Elimizdeki sınırlı veri. "Son 300 gün."
- **Parametre:** Evrenin gerçek (bilinmeyen) değeri. Örn. gerçek ortalama μ.
- **İstatistik:** Örneklemden hesapladığımız tahmin. Örn. örneklem ortalaması x̄.

Çıkarımsal istatistik = "x̄'den μ'ye dürüstçe nasıl atlarım?"

---

## 2. Örnekleme dağılımı ve standart hata

Farklı örneklemler farklı x̄ verir. Bu x̄'lerin dağılımı **örnekleme
dağılımı**dır ve (CLT sayesinde) yaklaşık normaldir.

**Standart hata (SE):** Örneklem ortalamasının standart sapması:
$$SE = \frac{\sigma}{\sqrt{n}}$$

> 🔑 **Kritik sezgi:** n arttıkça SE küçülür (√n hızında). 4 kat veri = 2 kat
> kesinlik. Bu yüzden daha çok veri her zaman daha güvenilirdir — ama getirisi
> azalır.

> ⚠️ Std (σ) ile SE'yi karıştırma: **Std** verinin yayılımıdır (sabit kalır).
> **SE** tahminimizin belirsizliğidir (veri arttıkça azalır).

---

## 3. Güven aralıkları (Confidence Interval, CI)

Tek bir sayı (nokta tahmin) yanıltıcıdır. Bunun yerine bir **aralık** veririz.

%95 CI (yaklaşık):
$$\bar{x} \pm 1.96 \times SE$$

```python
import numpy as np
from scipy import stats
veri = np.random.default_rng(1).normal(0.1, 2.5, 300)

x_bar = veri.mean()
se = veri.std(ddof=1) / np.sqrt(len(veri))
ci = stats.t.interval(0.95, df=len(veri)-1, loc=x_bar, scale=se)
print(f"Ortalama: {x_bar:.3f}, %95 CI: [{ci[0]:.3f}, {ci[1]:.3f}]")
```

> **Doğru yorum:** "Bu yöntemi defalarca uygulasaydım, ürettiğim aralıkların
> %95'i gerçek μ'yü içerirdi."
> **Yanlış yorum:** "Gerçek μ'nün bu aralıkta olma olasılığı %95." (Bu
> Bayesian "credible interval"dır — Modül 11. Frekansçı CI'da μ sabittir,
> rastgele olan aralıktır.)

---

## 4. Hipotez testi — "bu fark gerçek mi, şans mı?"

Bilimsel yöntemin istatistiksel hâli. Adımlar:

1. **H₀ (sıfır hipotezi):** "Hiçbir şey yok / fark sıfır." Çürütmeye çalıştığımız
   savunmacı varsayım. Örn. "Stratejinin getirisi 0."
2. **H₁ (alternatif):** İddiamız. "Getiri 0'dan büyük."
3. **Test istatistiği** hesapla (örn. t-skoru).
4. **p-değeri** bul.
5. p < α (genelde 0.05) ise H₀'ı **reddet**.

### p-değeri tam olarak nedir?
> **H₀ doğruyken**, gözlediğimiz kadar veya daha aşırı bir sonuç görme
> olasılığı.

Küçük p = "eğer gerçekten hiçbir şey olmasaydı, böyle bir veri görmem çok
şaşırtıcı olurdu" = H₀'a karşı kanıt.

> ⚠️ **p-değeri NE DEĞİLDİR:**
> - H₀'ın doğru olma olasılığı **değildir**.
> - Etkinin büyüklüğü **değildir** (büyük n'de minik, anlamsız farklar bile
>   p<0.05 verir).
> - p>0.05 "etki yok" demek **değildir** ("kanıt bulamadık" demektir).

---

## 5. İki tür hata ve güç

| | H₀ aslında doğru | H₀ aslında yanlış |
|---|---|---|
| **H₀'ı reddettik** | ❌ Tip I hata (α) — yanlış alarm | ✅ Doğru |
| **H₀'ı reddetmedik** | ✅ Doğru | ❌ Tip II hata (β) — kaçırma |

- **α (yanlış pozitif oranı):** Genelde 0.05. Olmayan etkiyi "var" deme riski.
- **Güç (power) = 1 − β:** Var olan etkiyi yakalama olasılığı. ≥0.80 hedeflenir.
- **Güç** ↑ olması için: örneklem ↑, etki büyüklüğü ↑, gürültü ↓.

> 💡 **Güç analizi** ile deneyden ÖNCE "kaç örnek lazım?" hesaplanır. Az
> örneklemli test, gerçek etkiyi kaçırır (düşük güç) — zaman kaybıdır.

---

## 6. Sık kullanılan testler — karar rehberi

| Soru | Test |
|---|---|
| Bir ortalama belli bir değerden farklı mı? | Tek örneklem **t-testi** |
| İki grubun ortalaması farklı mı? | Bağımsız iki örneklem **t-testi** |
| Aynı denekte önce/sonra farkı? | Eşleştirilmiş **t-testi** |
| 3+ grubun ortalamaları farklı mı? | **ANOVA** (F-testi) |
| İki kategorik değişken ilişkili mi? | **Ki-kare** bağımsızlık testi |
| Veri normal değil / sıralı | **Mann-Whitney U**, **Wilcoxon** (nonparametrik) |
| İki oran farklı mı (A/B test) | **z-testi / iki oran testi** |
| Veri normal mi? | **Shapiro-Wilk**, QQ-plot |

```python
from scipy import stats
# A/B test örneği: iki stratejinin getirileri farklı mı?
a = np.random.default_rng(1).normal(0.1, 2.0, 200)
b = np.random.default_rng(2).normal(0.4, 2.0, 200)

t, p = stats.ttest_ind(a, b, equal_var=False)  # Welch t-testi (güvenli varsayılan)
print(f"t={t:.2f}, p={p:.4f}")
print("Fark anlamlı" if p < 0.05 else "Anlamlı fark yok")
```

---

## 7. Etki büyüklüğü — "anlamlı ≠ önemli"

p-değeri farkın *var olup olmadığını* söyler; **ne kadar büyük** olduğunu değil.
Bunu **etki büyüklüğü** söyler:
- **Cohen's d:** İki ortalama farkının std cinsinden büyüklüğü (0.2 küçük,
  0.5 orta, 0.8 büyük).
- **R², korelasyon:** İlişkinin pratik gücü.

> Her zaman **p-değeri + etki büyüklüğü + güven aralığı** birlikte raporla.

---

## 8. Çoklu test problemi (p-hacking tehlikesi)

100 anlamsız strateji test edersen, şans eseri ~5 tanesi p<0.05 verir!
Bu "yanlış keşif"tir. Düzeltmeler:
- **Bonferroni:** α'yı test sayısına böl (katı).
- **Benjamini-Hochberg (FDR):** Yanlış keşif oranını kontrol et (daha dengeli).

> 🔑 Trading'de en büyük tuzaklardan biri: yüzlerce strateji/parametre deneyip
> "kazananı" seçmek. Bu, gürültüyü ezberlemektir — gelecekte çöker. Modül 08
> (overfitting) ve out-of-sample test şart.

---

## 🎯 Alıştırma

1. Stratejinin 300 günlük getirisinin ortalaması için %95 güven aralığını
   hesapla. Aralık 0'ı içeriyor mu? İçeriyorsa kârlılık istatistiksel olarak
   kanıtlanamamış demektir.
2. İki parametre setini (örn. RSI 14 vs RSI 21) Welch t-testiyle karşılaştır.
   Fark anlamlı mı? Cohen's d ile etki büyüklüğüne de bak.
3. 20 rastgele "strateji" üret (hepsi gerçekte gürültü). Kaç tanesi p<0.05
   veriyor? Bonferroni düzeltmesi uygula — kaç tanesi hayatta kalıyor?

---

## ✅ Kontrol listesi

- [ ] Std ile standart hatayı (SE) ayırıyorum.
- [ ] Güven aralığını doğru yorumluyorum (frekansçı vs Bayesian).
- [ ] p-değerinin ne olduğunu VE ne olmadığını söyleyebiliyorum.
- [ ] Tip I/II hata ve güç kavramlarını biliyorum.
- [ ] "İstatistiksel anlamlılık ≠ pratik önem" ilkesini içselleştirdim.
- [ ] Çoklu test / p-hacking tuzağının farkındayım.

Sonraki → [Modül 05: Lineer Regresyon](05-lineer-regresyon.md)
