# 📊 MegaStat — 8 Katmanlı Sınırsız İstatistik + ML Keşif Motoru

Veri dosyanızı verin (CSV / Excel / SPSS `.sav`), MegaStat **8 katmanlı tam analiz** yapsın.
Literatür yok, makale yok, üretken yapay zekâ yok — saf, deterministik istatistik + makine
öğrenmesi. PaperForge (`app/`) kodundan tamamen bağımsızdır.

## 8 Katman

| # | Katman | Ne bulur |
|---|---|---|
| 1 | **Betimseller + normallik** | her değişkenin tam profili (20+ ölçü), Shapiro-Wilk / D'Agostino + Lilliefors + Anderson-Darling + Jarque-Bera |
| 2 | **Klasik testler (sınırsız)** | tüm t/Welch/Mann-Whitney/ANOVA/Kruskal/ki-kare/Fisher/korelasyon çiftleri + etki büyüklükleri + Bonferroni/Holm/FDR |
| 3 | **Gelişmiş klasik testler** | eşleştirilmiş t / Wilcoxon (ön-son test), Friedman + Kendall W, Cohen kappa + McNemar (uyum), **Cronbach α + McDonald ω** güvenilirlik + madde analizi, **faktör analizi** (KMO, Bartlett, varimax), **çoklu doğrusal regresyon** (β, VIF), **lojistik regresyon** (OR + %95 GA), **ROC** (AUC, Youden kesim, duyarlılık/özgüllük) |
| 4 | **Doğrusal-olmayan gizli ilişkiler** | Karşılıklı Bilgi (Mutual Information): Pearson'ın düşük gösterdiği ama gerçekte güçlü (eğrisel/eşikli) bağlar |
| 5 | **ML öngörü (Gradient Boosting)** | her değişkeni diğerlerinden tahmin eden çapraz-doğrulamalı model + permütasyon önem sıralaması: "X'i asıl ne belirliyor?" |
| 6 | **Kısmi korelasyon** | üçüncü değişken kontrol edilince kaybolan **sahte/aracılı** ilişkiler ve güçlenen **baskılanmış** ilişkiler |
| 7 | **Gizli alt gruplar + sıra dışı vakalar** | PCA + K-Means kümeleme (silhouette kaliteli), Isolation Forest ile çok değişkenli anomali tespiti |
| 8 | **Risk skoru** | ikili sonuçlar (hasta/sağlam vb.) için çapraz-doğrulamalı risk modeli: AUC, risk belirleyicileri, en riskli vakalar |

Ayrıca: `TotalBilirubin↔İndirekBilirubin` gibi **apaçık/tanımsal korelasyonlar** (|r|≥0.95)
otomatik ayıklanıp ayrı sayfaya konur — gerçek keşifleri boğmazlar.

## Gelişmiş klasik katmanın (3) tam dökümü

| Kategori | İçerik |
|---|---|
| **Eşleştirilmiş testler** | **her sayısal çift için** eşleştirilmiş t + Wilcoxon işaretli sıra + Cohen d_z; fark normalliğine göre önerilen test (ön-test/son-test tasarımları) |
| **Tekrarlı ölçüm** | madde gruplarında (örn. `madde1..madde5`) Friedman ki-kare + Kendall W |
| **Uyum** | aynı düzeyli kategorik çiftler için Cohen kappa (+ 3+ düzeyde doğrusal ağırlıklı kappa), tam uyum %, 2×2'de McNemar |
| **Güvenilirlik** | Cronbach alfa + Feldt %95 GA, McDonald omega, iki-yarı + Spearman-Brown; madde analizi: madde-toplam r, silinirse-alfa |
| **Faktör analizi (AFA)** | KMO örneklem uygunluğu, Bartlett küresellik testi, özdeğerler, Kaiser ölçütü, varimax döndürülmüş yükler + ortak varyans (h²) |
| **Çoklu doğrusal regresyon** | **her sayısal bağımlı için** diğer sayısallarla OLS: B, SH, standardize β, %95 GA, VIF (çoklu bağlantı uyarısı), R², düzeltilmiş R², F |
| **Lojistik regresyon** | **her ikili kategorik sonuç için** sayısal yordayıcılarla: odds oranı + %95 GA, McFadden R², model AUC (yetersiz olay sayısında dürüstçe atlanır) |
| **ROC analizi** | **her ikili sonuç × sayısal belirteç için** AUC + Hanley-McNeil %95 GA, Youden J kesim noktası, kesimde duyarlılık/özgüllük, yön |

Ölçek maddeleri otomatik bulunur: sonu rakamla biten ortak önekli sütunlar (örn. `STAI_1..STAI_20`)
madde grubu sayılır; güvenilirlik, faktör ve Friedman analizleri bu gruplara uygulanır.

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
9. **Eşleştirilmiş Testler** — tüm sayısal çiftler için eşleştirilmiş t / Wilcoxon
10. **Tekrarlı Ölçüm (Friedman)** — madde gruplarında Friedman + Kendall W
11. **Uyum (Kappa-McNemar)** — aynı düzeyli kategorik çiftler
12. **Güvenilirlik (Alfa-Omega)** + **Madde Analizi** — ölçek güvenilirliği
13. **Faktör Analizi (KMO)** + **Faktör Yükleri** — AFA sonuçları
14. **Çoklu Regresyon** / **Lojistik Regresyon** / **ROC Analizi**
15. **Atlanan Testler** — örneklem yetersizliği vb. nedenlerle yapılamayanlar

## Güvenilirlik ilkeleri

- Tüm sayılar SciPy / statsmodels / pandas ile hesaplanır; yapay zekâ hiçbir sayı üretmez.
- Aynı veri her zaman aynı sonucu verir (deterministik).
- Binlerce test yapıldığı için ham p tek başına bırakılmaz; FDR düzeltmesi olmadan
  "anlamlı" damgası vurulmaz.
- Örneklemi yetersiz testler sessizce yanlış hesaplanmaz; **atlanır ve nedeni raporlanır**.
- Kimlik sütunları, sabit sütunlar ve serbest metin otomatik ayıklanır.
