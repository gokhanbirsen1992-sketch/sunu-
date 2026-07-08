# AlSat — Literatür Taraması

Bu belge, `alsat` modülündeki aday göstergelerin ve hakem (Reviewer 2) denetimlerinin
dayandığı akademik literatürün özetidir. Tarama 2026-07-08 tarihinde web araması ile
yapılmış; aşağıdaki kaynakların tamamı gerçek, yayımlanmış çalışmalardır.

## 1. Klasik piyasalarda teknik analiz kanıtı

- **Wilder, J. W. (1978).** *New Concepts in Technical Trading Systems.* Trend Research.
  → RSI (Göreli Güç Endeksi) ve ATR'nin orijinal tanımı. `gostergeler.rsi_esik` bu tanımı kullanır.
- **Brock, W., Lakonishok, J. & LeBaron, B. (1992).** "Simple Technical Trading Rules and the
  Stochastic Properties of Stock Returns." *Journal of Finance*, 47(5), 1731–1764.
  → Hareketli ortalama kesişimi ve **işlem aralığı kırılımı** (trading range breakout)
  kurallarının DJIA'da (1897–1986) istatistiksel öngörü gücü taşıdığını gösteren temel makale.
  `sma_kesisim`, `donchian_kirilim` aileleri buradan gelir.
- **Sullivan, R., Timmermann, A. & White, H. (1999).** "Data-Snooping, Technical Trading Rule
  Performance, and the Bootstrap." *Journal of Finance*, 54(5), 1647–1691.
  → BLL (1992) kurallarını White'ın Reality Check bootstrap'ıyla yeniden değerlendirir;
  veri madenciliği düzeltmesi sonrası kanıt zayıflar. Hakem denetimi **H5**'in gerekçesi.
- **White, H. (2000).** "A Reality Check for Data Snooping." *Econometrica*, 68(5), 1097–1126.
  → Çok sayıda strateji denendiğinde "en iyisinin" şans eseri iyi görünmesini test eden
  bootstrap çerçevesi. `olcutler.bootstrap_p` bunun basitleştirilmiş uyarlamasıdır.
- **Lo, A., Mamaysky, H. & Wang, J. (2000).** "Foundations of Technical Analysis." *Journal of
  Finance*, 55(4), 1705–1765. → Teknik örüntülerin bilgi içeriği taşıyabildiğine dair kanıt.
- **Park, C.-H. & Irwin, S. H. (2007).** "What Do We Know About the Profitability of Technical
  Analysis?" *Journal of Economic Surveys*, 21(4), 786–826.
  → 95 çalışmanın derlemesi: pozitif sonuç bildiren çalışmaların çoğunda **veri madenciliği,
  işlem maliyeti ihmali ve aşırı uyum** sorunları var. Reviewer 2 denetim listesinin (H1–H7)
  ana ilham kaynağı.

## 2. Momentum literatürü

- **Jegadeesh, N. & Titman, S. (1993).** "Returns to Buying Winners and Selling Losers."
  *Journal of Finance*, 48(1), 65–91. → Kesitsel momentumun temel makalesi.
- **Moskowitz, T., Ooi, Y. H. & Pedersen, L. H. (2012).** "Time Series Momentum." *Journal of
  Financial Economics*, 104(2), 228–250.
  → Bir varlığın **kendi geçmiş getirisinin işareti** gelecekteki getirisini öngörür (TSMOM);
  58 vadeli işlem piyasasında geçerli. `tsmom` göstergesinin kaynağı.
- **Barroso, P. & Santa-Clara, P. (2015).** "Momentum Has Its Moments." *Journal of Financial
  Economics*, 116(1), 111–120; **Daniel, K. & Moskowitz, T. (2016).** "Momentum Crashes."
  *JFE*, 122(2), 221–247. → Momentum çöküşleri ve volatilite ölçekleme çözümü.
- **Moreira, A. & Muir, T. (2017).** "Volatility-Managed Portfolios." *Journal of Finance*,
  72(4), 1611–1644. → Volatilite hedefleme riske göre düzeltilmiş getiriyi artırır.
  `vol_hedef` katmanının kaynağı.

## 3. Kripto piyasalarında teknik analiz

- **Detzel, A., Liu, H., Strauss, J., Zhou, G. & Zhu, Y. (2021).** "Learning and Predictability
  via Technical Analysis: Evidence from Bitcoin and Stocks with Hard-to-Value Fundamentals."
  *Financial Management*, 50(1), 107–137. (İlk sürüm 2018.)
  → BTC getirileri **5–100 günlük hareketli ortalamalarının fiyata oranıyla** öngörülebilir;
  temel değeri belirsiz varlıklarda yatırımcılar teknik sinyallerden "öğrenir". 1–2 haftalık
  ve 5–100 günlük MA pencereleri buradan.
- **Hudson, R. & Urquhart, A. (2021).** "Technical Trading and Cryptocurrencies." *Annals of
  Operations Research*, 297, 191–220.
  → BTC + 3 büyük kripto üzerinde **~15.000 teknik kural**; çoklu-hipotez düzeltmeleri
  sonrasında bile anlamlı öngörü/karlılık; alım-satım kuralları **uzun ve derin düşüşlere
  karşı koruma** sağlıyor; başabaş işlem maliyeti tipik kripto maliyetlerinin üstünde.
  ÖNEMLİ ihtiyat: BTC'de örneklem-dışı dönemde öngörü **zayıflıyor** → H6 denetiminin gerekçesi.
- **Grobys, K., Ahmed, S. & Sapkota, N. (2020).** "Technical Trading Rules in the
  Cryptocurrency Market." *Finance Research Letters*, 32, 101396.
  → Varyans-ağırlıklı MA stratejileri işlem maliyeti sonrası dahi kârlı (2016–2018).
- **Corbet, S., Eraslan, V., Lucey, B. & Sensoy, A. (2019).** "The Effectiveness of Technical
  Trading Rules in Cryptocurrency Markets." *Finance Research Letters*, 31, 32–37.
  → MA kesişim kurallarının BTC'de satın-al-tut'u geçebildiğine dair kanıt.
- **Liu, Y. & Tsyvinski, A. (2021).** "Risks and Returns of Cryptocurrency." *Review of
  Financial Studies*, 34(6), 2689–2727. → Kriptoda momentumun fiyatlanan bir etken olduğu;
  1–4 haftalık kısa pencereler kriptoda en güçlü momentum bölgesi.
- **Han, C., Kang, B. & Ryu, J. (2023, SSRN 4675565).** "Time-Series and Cross-Sectional
  Momentum in the Cryptocurrency Market: A Comprehensive Analysis under Realistic Assumptions."
  → Gerçekçi maliyet varsayımları altında kripto TSMOM incelemesi; maliyet varsayımlarının
  sonucu tersine çevirebildiğini gösterir → H3 (maliyet stresi) denetiminin gerekçesi.
- **Risk-managed momentum kripto çalışmaları (2024–2025,** ör. *Finance Research Letters*,
  "Cryptocurrency market risk-managed momentum strategies"; *FMPM* 2025 "Cryptocurrency
  momentum has (not) its moments"**)** → kripto momentumu ağır kuyruk çöküşlerine açık;
  **volatilite yönetimi** çöküşleri hafifletir. `vol_hedef` katmanının kriptoya uyarlanma gerekçesi.

## 4. Backtest aşırı uyumu ve çoklu test (Reviewer 2'nin silahları)

- **Bailey, D. H. & López de Prado, M. (2014).** "The Deflated Sharpe Ratio: Correcting for
  Selection Bias, Backtest Overfitting and Non-Normality." *Journal of Portfolio Management*,
  40(5), 94–107. → N deneme içinden en iyisini seçmenin Sharpe'ı şişirmesini düzelten
  **DSR**. `olcutler.deflated_sharpe` doğrudan bu formülü uygular (çarpıklık/basıklık dahil).
- **Bailey, D. H., Borwein, J., López de Prado, M. & Zhu, Q. J. (2014).** "Pseudo-Mathematics
  and Financial Charlatanism: The Effects of Backtest Overfitting on Out-of-Sample
  Performance." *Notices of the AMS*, 61(5), 458–471. → Aşırı uyumun OOS performansı nasıl
  yok ettiğinin matematiği; walk-forward zorunluluğunun gerekçesi.
- **Harvey, C. R. & Liu, Y. (2015).** "Backtesting." *Journal of Portfolio Management*, 42(1),
  13–28; **Harvey, C. R., Liu, Y. & Zhu, H. (2016).** "…and the Cross-Section of Expected
  Returns." *RFS*, 29(1), 5–68. → Çoklu test düzeltmesi yapılmadan bildirilen t-istatistikleri
  güvenilmez; "faktör hayvanat bahçesi" eleştirisi.

## 5. Tasarım kararlarına çeviri

| Literatür bulgusu | alsat'taki karşılığı |
|---|---|
| MA/kırılım kuralları öngörü taşır (BLL 1992; Detzel 2021; Grobys 2020) | Aday havuzu: `sma_kesisim`, `fiyat_sma`, `donchian_kirilim`, `macd_kural` |
| Kriptoda momentum kısa pencerede güçlü (Liu-Tsyvinski 2021) | `tsmom` 7–90 gün pencereler |
| Momentum çöker; vol yönetimi kurtarır (Barroso 2015; Moreira-Muir 2017; FRL 2025) | `vol_hedef` düzeltme eylemi (hakem önerisi V) |
| Tek kural kırılgan; kural sınıfları birlikte daha sağlam (Hudson-Urquhart 2021) | `topluluk` (oy) düzeltme eylemi |
| Veri madenciliği en iyi kuralı şişirir (White 2000; Sullivan 1999; Bailey-LdP 2014) | DSR + bootstrap p + H5 denetimi; aday sayısı kayıt altında |
| Maliyet ihmal edilirse sonuç tersine döner (Park-Irwin 2007; Han 2023) | bps maliyet + kayma her işlemde; H3 2×/4× maliyet stresi |
| OOS bozulması tipik (Hudson-Urquhart BTC OOS; Bailey 2014) | Walk-forward zorunlu; H6 IS→OOS bozulma denetimi |

## Dürüstlük notu

Bu literatürün bütünsel mesajı: teknik kurallar *bazı* piyasa ve dönemlerde, *maliyet ve
çoklu-test düzeltmesinden sonra bile* öngörü taşıyabilir; ancak hiçbir kural kalıcı kâr
garantisi vermez ve en güçlü bulgular bile örneklem-dışında zayıflar. `alsat`ın amacı kâr
vaat etmek değil, **bu denetimlerden sağ çıkan en savunulabilir kuralı** bulmak ve
sağ çıkamıyorsa bunu açıkça raporlamaktır.
