---
name: spss-kesif
description: >
  Bir SPSS (.sav) veya CSV/Excel veri dosyasında, klasik SPSS'in göremediği
  GİZLİ örüntüleri keşfeder: doğrusal-olmayan ilişkiler, otomatik etkileşimler,
  nedensel etkiler (EconML), gizli alt-gruplar/segmentler, anomaliler ve
  doğrusal-olmayan değişken ağı. Modern ML (gradient boosting, SHAP, causal ML,
  denetimsiz öğrenme) kullanır AMA her bulguyu yayına uygunluk için titizlikle
  eler (holdout doğrulama, çoklu-test düzeltmesi, etki büyüklüğü, sızıntı
  kontrolü). Kullanıcı bir .sav dosyası verip "gizli ilişkileri bul",
  "SPSS'in yapamadığı analizleri yap", "yayına aday bulgu çıkar" gibi
  istediğinde kullan.
---

# SPSS-K,eşif — SPSS'in Ötesinde İstatistiksel Keşif Motoru

## Bu skill ne yapar?

Klasik SPSS testleri (t-test, ANOVA, lineer/lojistik regresyon, korelasyon)
**önceden belirttiğin** ilişkileri ve **doğrusal** etkileri test eder. Bu skill,
veride **kendiliğinden** gizli yapıları arar:

| Klasik SPSS | Bu skill (modern ML) |
|---|---|
| Doğrusal ilişki (y = a + bx) | **Doğrusal-olmayan** ilişkiler (eşik, doygunluk, U-şekli) |
| Etkileşimi sen yazarsın | Etkileşimleri **otomatik keşfeder** (SHAP interaction) |
| "Ortalama etki" | **Kime ne kadar** etki eder (heterojen etki / CATE) |
| Korelasyon (sadece doğrusal) | **Mutual information** ağı (her tür ilişki) |
| Kontrol değişkenini sen seçersin | **Nedensel etki** (DML ile confounder kontrolü) |
| Aykırı = elle bak | **Anomali tespiti** (çok boyutlu) |
| Grupları sen tanımlarsın | **Gizli segmentleri** keşfeder (kümeleme) |

## ⚠️ EN ÖNEMLİ KURAL — yayın titizliği

"Gizli ilişki" bulmak kolaydır; çoğu **gürültüdür**. Bu skill her bulguyu
şu süzgeçlerden geçirir ve **doğrulanmamış hiçbir şeyi "bulgu" diye sunmaz**:

1. **Keşif/Doğrulama ayrımı:** Veri ikiye bölünür. Örüntüler **keşif (train)**
   setinde aranır, **doğrulama (holdout)** setinde teyit edilir. Sadece her
   ikisinde de duran örüntü raporlanır.
2. **Çoklu-test düzeltmesi:** Yüzlerce ilişki test edilince bazıları şans eseri
   "anlamlı" çıkar. Benjamini-Hochberg (FDR) ile düzeltilir.
3. **Etki büyüklüğü:** p-değeri değil, **pratik büyüklük** (R², SHAP katkısı,
   etki aralığı) raporlanır. "Anlamlı ≠ önemli."
4. **Sızıntı kontrolü:** Hedefi kopyalayan/geleceğe bakan değişkenler işaretlenir.
5. **Belirsizlik:** Tahminlere güven/credible aralık eklenir.
6. **Nedensellik uyarısı:** ML örüntü bulur; nedensel iddia AÇIKÇA varsayım
   gerektirir — skill bunu her zaman not düşer.

> Skill'in çıktısı = **yayına ADAY hipotezler + titizlik raporu.** Gerçek yayın
> için bulguların yeni/bağımsız veriyle (ideal: ön-kayıtlı) doğrulanması şarttır.

## Ne zaman kullanılır

- Kullanıcı `.sav` / `.csv` / `.xlsx` veri dosyası verir.
- "SPSS'in yapamadığı analiz", "gizli ilişki/örüntü bul", "doğrusal olmayan
  etkiler", "kime etki ediyor", "yayına aday bulgu", "veri madenciliği" der.

## İş akışı (bu adımları izle)

### 0. Kurulum (gerekirse)
```bash
pip install pyreadstat pandas numpy scipy scikit-learn \
            xgboost lightgbm catboost shap statsmodels \
            umap-learn econml  # econml/umap opsiyonel
```

### 1. Veriyi yükle ve profille
`analyze.py`'deki `load_data()` + `profile()` ile dosyayı oku (değer
etiketlerini koru), değişken tiplerini çıkar, eksik veriyi raporla.
**Kullanıcıya değişken listesini göster** ve sor:
- Hangi değişken(ler) **sonuç/hedef** (Y)? (Yoksa skill tümünü tarar.)
- Nedensel analiz isteniyorsa hangisi **müdahale/tedavi** (T)?
- Hariç tutulacak ID/tarih sütunları var mı?

### 2. Keşif modüllerini çalıştır
`analyze.py` tek komutla tüm modülleri (train/holdout bölünmüş) çalıştırır:
```bash
python analyze.py veri.sav --target HEDEF_DEGISKEN --out rapor/
```
Modüller: doğrusal-olmayan ilişki + önem (boosting+SHAP), etkileşim keşfi,
gizli segment (kümeleme), anomali, MI ağı, (opsiyonel) nedensel etki (DML).

### 3. Bulguları ELE ve raporla
Üretilen `rapor/bulgular.md` dosyasını oku. Her aday bulgu için:
- Holdout'ta teyit edildi mi? FDR sonrası ayakta mı? Etki büyüklüğü anlamlı mı?
- Doğrulananları "güçlü bulgu", teyit edilemeyenleri "şüpheli/gürültü" diye ayır.
- Her bulguyu **sade dille + uyarılarıyla** kullanıcıya sun.

### 4. Yayın yol haritası
Güçlü bulgular için kullanıcıya öner: bağımsız veriyle doğrulama, ön-kayıt,
nedensel varsayımların tartışılması, uygun istatistiksel raporlama (etki
büyüklüğü + GA), sınırlılıklar bölümü.

## Dosyalar
- `analyze.py` — tüm keşif motoru (modüler, opsiyonel bağımlılıklara dayanıklı).
- `README.md` — ayrıntılı kullanım, modül açıklamaları, örnekler.

## Altın ilke
**Yöntem parlaklığı değil, doğrulama yayın yapar.** Bu skill çok güçlü örüntü
bulucudur; gücünü sorumlulukla kullan — bulduğun her şeyi kırmaya çalış,
ayakta kalanı raporla.
