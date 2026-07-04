# 📊 MegaStat — 7 Katmanlı Sınırsız İstatistik + ML Keşif Motoru

Veri dosyanızı verin (CSV / Excel / SPSS `.sav`), MegaStat **7 katmanlı tam analiz** yapsın.
Literatür yok, makale yok, üretken yapay zekâ yok — saf, deterministik istatistik + makine
öğrenmesi. PaperForge (`app/`) kodundan tamamen bağımsızdır.

## 7 Katman

| # | Katman | Ne bulur |
|---|---|---|
| 1 | **Betimseller + normallik** | her değişkenin tam profili (20+ ölçü), Shapiro-Wilk / D'Agostino |
| 2 | **Klasik testler (sınırsız)** | tüm t/Welch/Mann-Whitney/ANOVA/Kruskal/ki-kare/Fisher/korelasyon çiftleri + etki büyüklükleri + Bonferroni/Holm/FDR |
| 3 | **Doğrusal-olmayan gizli ilişkiler** | Karşılıklı Bilgi (Mutual Information): Pearson'ın düşük gösterdiği ama gerçekte güçlü (eğrisel/eşikli) bağlar |
| 4 | **ML öngörü (Gradient Boosting)** | her değişkeni diğerlerinden tahmin eden çapraz-doğrulamalı model + permütasyon önem sıralaması: "X'i asıl ne belirliyor?" |
| 5 | **Kısmi korelasyon** | üçüncü değişken kontrol edilince kaybolan **sahte/aracılı** ilişkiler ve güçlenen **baskılanmış** ilişkiler |
| 6 | **Gizli alt gruplar + sıra dışı vakalar** | PCA + K-Means kümeleme (silhouette kaliteli), Isolation Forest ile çok değişkenli anomali tespiti |
| 7 | **Risk skoru** | ikili sonuçlar (hasta/sağlam vb.) için çapraz-doğrulamalı risk modeli: AUC, risk belirleyicileri, en riskli vakalar |

Ayrıca: `TotalBilirubin↔İndirekBilirubin` gibi **apaçık/tanımsal korelasyonlar** (|r|≥0.95)
otomatik ayıklanıp ayrı sayfaya konur — gerçek keşifleri boğmazlar.

## Klasik katmanın (1-2) tam dökümü

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

### Render.com'a kurulum (kurulumsuz, telefondan kullanım)

Depodaki `render.yaml` artık **iki servis** içerir: `paperforge` (makale pipeline'ı) ve
`megastat` (bu araç). Kurulum:

1. <https://render.com> → GitHub ile giriş yapın.
2. **New + → Blueprint** → bu depoyu (`gokhanbirsen1992-sketch/sunu-`) seçin.
3. Dal (branch) ekranında `render.yaml`'ın bulunduğu dalı seçin ve onaylayın.
4. Dakikalar içinde `https://megastat-XXXX.onrender.com` gibi bir adres alırsınız —
   telefonunuzdan bu adrese girip dosya yükleyerek analiz yapabilirsiniz.

Not: Ücretsiz planda servis 15 dakika boş kalınca uyur; ilk açılış ~1 dakika sürebilir.
Sadece MegaStat isterseniz Blueprint yerine **New + → Web Service** ile depoyu seçip
başlatma komutu olarak `uvicorn megastat.web:app --host 0.0.0.0 --port $PORT` yazmanız yeterli.

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
