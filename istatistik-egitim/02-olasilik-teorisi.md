# Modül 02 — Olasılık Teorisi

> **Hedef:** Belirsizliği sayıya dökmek. Tüm istatistik ve makine öğrenmesi,
> olasılığın üzerine kuruludur. Özellikle **Bayes kuralı** ileride (Modül 11)
> tüm Bayesian dünyanın temeli olacak.

---

## 1. Temel kavramlar

- **Deney:** Sonucu belirsiz bir süreç (zar atmak, yarınki fiyat).
- **Örnek uzay (S):** Tüm olası sonuçlar. Zar için S = {1,2,3,4,5,6}.
- **Olay (event):** Örnek uzayın bir alt kümesi. "Çift sayı" = {2,4,6}.
- **Olasılık P(A):** 0 ile 1 arası bir sayı. 0 = imkânsız, 1 = kesin.

### Kolmogorov aksiyomları (olasılığın 3 kuralı)
1. P(A) ≥ 0 (negatif olamaz).
2. P(S) = 1 (bir şey mutlaka olur).
3. Ayrık olaylar için P(A veya B) = P(A) + P(B).

---

## 2. Olasılık hesaplama kuralları

- **Tümleyen:** P(A olmaz) = 1 − P(A). Çoğu zaman "en az bir" problemini
  "hiç olmaması"ndan hesaplamak kolaydır.

- **Toplama kuralı (birleşim):**
  $$P(A \cup B) = P(A) + P(B) - P(A \cap B)$$
  Kesişimi çıkarırız çünkü iki kez saymışızdır.

- **Çarpım kuralı (kesişim):**
  $$P(A \cap B) = P(A)\,P(B \mid A)$$

---

## 3. Koşullu olasılık — "bilgi olasılığı değiştirir"

$$P(A \mid B) = \frac{P(A \cap B)}{P(B)}$$

"B gerçekleştiğini bildiğimde A'nın olasılığı." Örnek uzayı B'ye daraltırız.

> **Sezgi:** Genel nüfusta hastalık olasılığı %1. Ama testin pozitif çıktığını
> *bilirsen* bu olasılık değişir. İşte tüm teşhis, spam filtresi ve risk
> modellemesi bu fikre dayanır.

### Bağımsızlık
A ve B bağımsızsa, birinin olması diğerini etkilemez:
$$P(A \mid B) = P(A) \quad\Longleftrightarrow\quad P(A \cap B) = P(A)P(B)$$

> ⚠️ Finansta tuzak: "Her gün bağımsız" varsaymak yanlıştır — oynaklık
> kümelenir (bugün dalgalıysa yarın da dalgalı olma eğilimindedir, Modül 12 GARCH).

---

## 4. Bayes Kuralı — istatistiğin en güçlü tek formülü

$$\boxed{P(A \mid B) = \frac{P(B \mid A)\,P(A)}{P(B)}}$$

Koşulu **tersine çevirir**: "B verildiğinde A"yı, "A verildiğinde B"den hesaplar.

- **P(A)** = önsel (prior) — veriyi görmeden önceki inanç.
- **P(B|A)** = olabilirlik (likelihood) — A doğruysa B'yi görme şansı.
- **P(A|B)** = sonsal (posterior) — veriyi gördükten sonraki inanç.
- **P(B)** = kanıt (evidence) — normalizasyon sabiti.

### Klasik örnek: tıbbi test (sezgini sarsacak)
- Hastalık nadir: P(hasta) = %1.
- Test iyi: hastaysan %99 pozitif (P(+|hasta)=0.99), sağlıklıysan %5 yanlış
  pozitif (P(+|sağlıklı)=0.05).
- **Soru:** Pozitif çıktın. Gerçekten hasta olma ihtimalin?

$$P(\text{hasta}\mid +) = \frac{0.99 \times 0.01}{0.99\times0.01 + 0.05\times0.99} = \frac{0.0099}{0.0594} \approx 0.167$$

**Sadece %17!** İnsanların çoğu %99 sanır. Sebep: hastalık o kadar nadir ki,
yanlış pozitifler gerçek pozitifleri ezer. **Taban oranı (base rate) önemlidir.**

```python
P_hasta = 0.01
P_poz_hasta = 0.99
P_poz_saglikli = 0.05
P_poz = P_poz_hasta*P_hasta + P_poz_saglikli*(1-P_hasta)
print(P_poz_hasta*P_hasta / P_poz)   # 0.1666...
```

---

## 5. Rastgele değişkenler (RV)

Deneyin sonucunu sayıya eşleyen fonksiyon. İki tip:

- **Kesikli:** Sayılabilir değerler (zar=1..6, gün içi işlem sayısı).
  - **PMF** (olasılık kütle fonksiyonu): P(X = x).
- **Sürekli:** Aralıktaki her değer (fiyat, süre).
  - **PDF** (olasılık yoğunluk fonksiyonu): tek bir noktanın olasılığı 0'dır;
    olasılık **alan** olarak (integralle) hesaplanır.
- **CDF** (kümülatif dağılım): F(x) = P(X ≤ x). Her iki tip için de geçerli.

---

## 6. Beklenen değer ve varyans

- **Beklenen değer (E[X]):** Uzun vadeli ortalama, "olasılıkla ağırlıklı toplam".
  $$E[X] = \sum_x x\,P(X=x) \quad\text{veya}\quad \int x\,f(x)\,dx$$

  > **Sezgi:** Bir bahsin E[X]'i pozitifse uzun vadede kazandırır. Kumarhaneler
  > E[X]<0 olduğu için *daima* kazanır. Trading'de "edge" = pozitif beklenen değer.

- **Varyans:** Var(X) = E[(X − E[X])²] = E[X²] − (E[X])². Risk/belirsizlik ölçüsü.

### Yararlı özellikler
- E[aX + b] = a·E[X] + b (doğrusaldır).
- Var(aX + b) = a²·Var(X) (sabit eklemek varyansı değiştirmez!).
- **Bağımsız** X, Y için: E[X+Y]=E[X]+E[Y], Var(X+Y)=Var(X)+Var(Y).

> 💡 Portföy çeşitlendirmesinin matematiği budur: bağımsız (korelasyonsuz)
> varlıkları toplayınca getiri toplanır ama risk (std) karekök hızında büyür →
> riski düşürürsün.

---

## 7. Büyük Sayılar Yasası (LLN)

Örneklem büyüdükçe **örneklem ortalaması → gerçek beklenen değere** yaklaşır.
Yazı-tura 10 atışta %70 tura gelebilir, ama 100.000 atışta ~%50'ye oturur.

> Bu yasa olmadan hiçbir istatistik çalışmazdı: az veriden yanılırız, çok
> veriden gerçeğe yaklaşırız.

---

## 🎯 Alıştırma

1. Bir trading stratejisi işlemlerin %40'ında +%3, %60'ında −%1 getiriyor.
   Beklenen değeri hesapla. Strateji kârlı mı? (İpucu: 0.4·3 + 0.6·(−1))
2. Bayes kuralıyla: bir "AL" sinyali geçmişte yükselişlerin %70'inde, ama
   düşüşlerin de %30'unda çıkmış. Piyasa genelde %50 yükseliyor. Sinyal
   çıktığında gerçekten yükseliş olasılığı nedir?
3. İki bağımsız varlığın her birinin std'si %2. Eşit ağırlıklı portföyün
   std'sini hesapla. Tek varlıktan düşük mü? Neden?

---

## ✅ Kontrol listesi

- [ ] Koşullu olasılık ile bağımsızlığı ayırt edebiliyorum.
- [ ] Bayes kuralını bir teşhis problemine uygulayabiliyorum.
- [ ] Taban oranının (base rate) neden önemli olduğunu anlıyorum.
- [ ] Beklenen değerin "edge" kavramıyla bağını kuruyorum.

Sonraki → [Modül 03: Olasılık Dağılımları](03-olasilik-dagilimlari.md)
