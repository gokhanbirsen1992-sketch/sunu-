# Otomatik İstatistik → Literatür → Makale Fikri

CSV / Excel / SPSS dosyası yükle → tüm değişkenler için **bivariate analiz** (FDR düzeltmeli) → anlamlı olanlar için **multivariate / Cox regresyon** → bulgulara göre **PubMed literatür araması** → makale kurgusu için **markdown rapor**.

## Özellikler

- 📁 **Çoklu format**: CSV, TSV, XLSX, SPSS (`.sav`), Stata (`.dta`)
- 🔍 **Otomatik tip tespiti**: sürekli / kategorik / sıralı / ikili (kullanıcı düzenleyebilir)
- 📊 **Bivariate**: Pearson/Spearman, t-test/Mann-Whitney, ANOVA/Kruskal, Chi²/Fisher — testi otomatik seçer, **FDR-Benjamini-Hochberg** ile çoklu karşılaştırma düzeltmesi
- 🔬 **Multivariate**:
  - Sürekli outcome → çoklu lineer regresyon
  - İkili outcome → lojistik regresyon (OR + %95 GA)
  - Sağkalım → Cox PH + Kaplan-Meier (log-rank)
  - VIF ile multikolineerlik kontrolü
- 📚 **PubMed E-utilities** ile literatür araması (her bulgu için)
- 📝 **Markdown rapor** + opsiyonel **Claude API** ile makale fikri üretimi

## Kurulum

```bash
pip install -r requirements.txt
```

## Çalıştırma

```bash
streamlit run app.py
```

Tarayıcıda açılan arayüzde 7 adımı sırayla takip edin.

## API anahtarları (opsiyonel)

- **PubMed API key** — hız sınırını yükseltir (3/sn → 10/sn). Almak için: https://www.ncbi.nlm.nih.gov/account/
- **Anthropic API key** — Claude ile makale kurgu önerisi üretmek için

İkisi de isteğe bağlı; uygulama anahtar olmadan da çalışır.

## Mimari

```
app.py                  Streamlit 7-adım sihirbaz
core/
  data_loader.py        CSV/SPSS/Excel okuma + impute
  auto_typer.py         sütun tipi tespiti
  bivariate.py          tüm test seçimi + FDR
  multivariate.py       lineer/lojistik regresyon
  survival.py           Cox + Kaplan-Meier (lifelines)
  literature.py         PubMed E-utilities
  report.py             markdown + LLM rapor
```

## Birleştirilen kütüphaneler

- **pandas / pyreadstat** — veri okuma
- **scipy / statsmodels / pingouin** — istatistik testleri
- **statsmodels** — regresyon
- **lifelines** — sağkalım analizi
- **biopython / requests** — PubMed E-utilities
- **streamlit** — web arayüzü
- **anthropic** — opsiyonel LLM rapor

## Sınırlamalar

- Tek değişkenli imputation (median/mode); MICE/IterativeImputer entegrasyonu sonraya
- Propensity score matching ve IPTW yok — gözlemsel veri için manuel ayar gerekli
- paper-qa entegrasyonu yok (PDF tabanlı RAG); şu an sadece PubMed metadata
- Forest plot grafiği yok — coefficients tablosu CSV olarak indirilebilir
