# 📊 MegaStat — Sınırsız İstatistik Motoru

Veri dosyanızı verin (CSV / Excel / SPSS `.sav`), MegaStat **hesaplanabilecek her istatistiği**
hesaplasın. Literatür yok, makale yok, yapay zekâ yok — sadece saf, deterministik istatistik.
PaperForge (`app/`) kodundan tamamen bağımsızdır.

## Ne hesaplar?

| Kategori | İçerik |
|---|---|
| **Betimseller (sayısal)** | n, eksik, ortalama, SS, SH, %95 GA, medyan, Q1/Q3, IQR, min/maks, aralık, çarpıklık, basıklık, varyasyon katsayısı, aykırı değer sayısı, normallik testi (Shapiro-Wilk / D'Agostino) |
| **Betimseller (kategorik)** | tüm düzey frekansları + yüzdeler, eşit dağılım ki-kare uyum testi |
| **Sayısal × Sayısal** | **her çift için** Pearson (+%95 GA), Spearman, Kendall, doğrusal regresyon (eğim, sabit, R²), ilişki gücü yorumu |
| **Kategorik × Sayısal** | **her çift için** — 2 grup: Student t + Welch t + Mann-Whitney + Cohen d + Hedges g + sıra çiftserisi r; 3+ grup: ANOVA + Welch ANOVA + Kruskal-Wallis + eta² + epsilon² + **Tukey / Mann-Whitney post-hoc** |
| **Kategorik × Kategorik** | **her çift için** ki-kare + Cramér V (+ 2×2'de Fisher exact + odds oranı), beklenen<5 hücre uyarısı |
| **Varsayım kontrolleri** | grup bazında normallik, Levene varyans eşitliği → **önerilen doğru test** otomatik işaretlenir |
| **Çoklu test düzeltmesi** | tüm p-değerlerine Bonferroni + Holm + Benjamini-Hochberg (FDR); "FDR sonrası anlamlı" sütunu |

Test sayısında **sınır yoktur**: değişken çifti kaç taneyse hepsi hesaplanır.
Örnek: 49 sütunluk bir dosyada tek komutla ~30.000 istatistik üretilir.

## Kullanım

### Komut satırı

```bash
pip install -r requirements.txt
python -m megastat veri.sav                 # rapor: veri_megastat.xlsx
python -m megastat veri.csv -o rapor.xlsx   # çıktı adını kendiniz seçin
```

### Telefon / tarayıcı

```bash
uvicorn megastat.web:app --host 0.0.0.0 --port 8000
```

Tarayıcıdan adrese girin → dosyayı yükleyin → özet ekranda, tam rapor Excel olarak iner.

## Excel raporu sayfaları

1. **Özet** — kaç satır/sütun/test/istatistik, kaç anlamlı bulgu
2. **Anlamlı Bulgular** — FDR düzeltmesi sonrası ayakta kalan her şey, p'ye göre sıralı
3. **Değişkenler** — hangi sütun nasıl sınıflandı, hangileri neden atlandı
4. **Betimsel (Sayısal / Kategorik)**
5. **Korelasyonlar** — tüm sayısal çiftler
6. **Grup Karşılaştırmaları** — tüm kategorik × sayısal çiftler
7. **Post-Hoc** — anlamlı çok-gruplu testlerin ikili karşılaştırmaları
8. **Kategorik İlişkiler** — tüm kategorik çiftler
9. **Atlanan Testler** — örneklem yetersizliği vb. nedenlerle yapılamayanlar

## Güvenilirlik ilkeleri

- Tüm sayılar SciPy / statsmodels / pandas ile hesaplanır; yapay zekâ hiçbir sayı üretmez.
- Aynı veri her zaman aynı sonucu verir (deterministik).
- Binlerce test yapıldığı için ham p tek başına bırakılmaz; FDR düzeltmesi olmadan
  "anlamlı" damgası vurulmaz.
- Örneklemi yetersiz testler sessizce yanlış hesaplanmaz; **atlanır ve nedeni raporlanır**.
- Kimlik sütunları, sabit sütunlar ve serbest metin otomatik ayıklanır.
