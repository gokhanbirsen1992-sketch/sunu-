# AlSat — Reviewer 2 Döngüsü Koşu Raporu

**Tarih:** 2026-07-08 · **Veri:** BTCUSDT (2010-07-18 → 2026-05-23, 5.789 gün) ve
ETHUSDT (2015-08-08 → 2026-05-23, 3.942 gün), günlük kapanış, Coin Metrics topluluk
verisi (GitHub; Binance/Crypto.com bu ortamın ağ politikasında engelliydi — `veri.py`
zinciri yerelde önce Binance'i dener). · **Maliyet:** 20 bps tek yön (komisyon + kayma).
· **Sınama:** genişleyen pencereli walk-forward; eğitim ≥ 3 yıl, test = takvim yılı;
sinyaller +1 gün gecikmeli uygulanır. Rapor edilen tüm sayılar **örneklem-dışıdır (OOS)**
ve *seçim prosedürünün* performansıdır (her yıl, yalnızca o yıldan önceki veriyle
seçilen kural o yıla uygulanır).

Excel eki: `alsat/alsat_rapor.xlsx` (tur özetleri, tüm eleştiriler, aday tabloları,
yıllık seçimler, özsermaye eğrileri).

---

## Tur 1 — geniş tarama (24 aday, 8 kural ailesi)

- **Seçilen:** `donchian_kirilim(giris=20, cikis=10)` — 14 test yılının 11'inde eğitim
  verisi bağımsız olarak aynı kuralı seçti (2013'te SMA 5/20, 2014'te fiyat/SMA-5,
  2018'de SMA 5/20).
- **OOS:** Sharpe **1.41**, yıllık getiri %85, maks düşüş **-%74**, DSR 1.00,
  bootstrap p < 0.001.
- **Reviewer 2 eleştirileri:**
  - **[uyarı] H1 uygulama gecikmesi:** sinyal aynı gün uygulansaydı Sharpe 3.06 olurdu.
    Kural kapanışa yakın bilgiye duyarlı; gecikmeli uygulama (bizim yaptığımız) doğru
    ve muhafazakâr olan.
  - K4 sağlanamadı: -%74 düşüş, satın-al-tut'un -%88'inin %80'inden (-%70,4) derin.
- **Post-mortem:** yüksek devirli adaylar (günde sık sinyal değiştiren RSI/MACD türevleri)
  seçim havuzunda gürültü yaratıyor; H1 önerisiyle **devir_azalt** uygulandı → medyan
  üstü devirli adaylar elendi (24 → 12).

## Tur 2 — düşük devirli havuz (12 aday)

- **Seçilen:** yine `donchian_kirilim(giris=20, cikis=10)` — bu kez 14/14 yılda.
- **OOS:** Sharpe **1.64**, yıllık getiri %99,4, maks düşüş **-%65**, DSR **1.00**,
  bootstrap p < 0.001, 2× maliyette OOS getirisi pozitif.
- **Reviewer 2:** H1 uyarısı sürüyor (3.19'a karşı 1.64 — bilgi olarak raporda);
  **[bilgi] H7:** -%65 düşüş, satın-al-tut'un -%88'ine karşı belirgin koruma
  (Hudson-Urquhart 2021 bulgusuyla uyumlu).
- **Kabul kriterleri: 5/5 → KABUL.**

| Kriter | Eşik | Sonuç |
|---|---|---|
| K1 OOS net Sharpe | > 0.5 ve her sembolde > 0 | 1.64; BTC 1.53 / ETH 0.98 ✓ |
| K2 Deflated Sharpe Ratio | ≥ 0.95 (24 kümülatif deneme düzeltmeli) | 1.00 ✓ |
| K3 2× maliyet stresi | OOS toplam getiri > 0 | ✓ |
| K4 Maks düşüş | < 0.8 × satın-al-tut düşüşü | -%65 < -%70,4 ✓ |
| K5 Hakem engeli | engel düzeyi eleştiri yok | ✓ |

**Sağlamlık göstergesi:** Tur 2 aday tablosunda *tüm* trend ailesi 1.27–1.64 Sharpe
bandında (SMA/EMA kesişimleri, TSMOM 60-90, fiyat/SMA-100, Donchian 55/20 ve 100/50).
Performans tek bir parametre tepeciğine değil geniş bir platoya dayanıyor — H2
(parametre hassasiyeti) denetiminin ateşlenmemesinin nedeni bu.

---

## Final indikatör

> **Donchian kanal kırılımı — giriş 20 gün, çıkış 10 gün (günlük kapanış, long/flat)**
> - **AL:** kapanış, önceki 20 günün en yüksek kapanışını aşarsa (ertesi gün uygulanır)
> - **SAT:** kapanış, önceki 10 günün en düşük kapanışının altına inerse (ertesi gün)
> - aksi hâlde pozisyon korunur.

Bağımsız kullanım: `alsat/final_indikator.py` (yalnız pandas/numpy;
`al_sat_sinyali(kapanis)` ve `son_karar(kapanis)`). Bu dosya, döngünün raporladığı
birleşik OOS Sharpe 1.64'ü bağımsız olarak yeniden üretir.

**TradingView:** `alsat/pine/alsat_donchian_indikator.pine` (grafikte AL/SAT okları +
uyarılar) ve `alsat/pine/alsat_donchian_strateji.pine` (TradingView backtest'i; emirler
ertesi barın açılışında dolar — Python'daki +1 gün gecikmenin karşılığı). Pine Editor'e
yapıştırıp **günlük (1D)** grafikte kullanın; strateji sürümündeki komisyon/kayma
değerlerini kendi borsanıza göre ayarlayın.

Kural yeni değildir — BLL (1992) "trading range break" kuralının ve Donchian/Turtle
geleneğinin kendisidir; bu çalışmanın katkısı kuralı *icat etmek* değil, 8 aile ve
24 aday arasından **çoklu-test düzeltmeli, maliyetli, walk-forward** bir yarışmada
hayatta kalanın bu olduğunu göstermektir.

## Koşu 2 (2026-07-08) — kullanıcı geri bildirimi üzerine sertleştirilmiş kriterler

Kullanıcı gözlemi: kural başka bir sembolde denendi ve "hep zararda" görünüyor
(TradingView'da *Percent Profitable* ≈ %40). İki tespit:

1. **%40 isabet oranı kırılım sistemlerinde normaldir** — çok sayıda küçük zarar,
   az sayıda büyük trend kazancı. Karlılığın ölçüsü isabet oranı değil, tüm dönem
   **net kârdır**. Yine de bu gözlem, doğrulamanın yalnızca BTC+ETH'de yapılmış
   olmasının gerçek bir zayıflık olduğunu gösterdi.
2. Bu koşuda döngü sertleştirildi: **H8 "güncel rejim" denetimi** (son 24 ayda hem
   mutlak hem göreli kayıp → engel) ve **K6 kabul kriteri** (son 24 ayda mutlak
   kazanç veya satın-al-tut'a üstünlük) eklendi; evren **5 sembole** çıkarıldı
   (BTC, ETH, BNB, XRP, ADA).

Sonuç (3 tur): Tur 1–2'de H8 uyarısı ve K4 düşüş kriteri takıldı; düzeltmeler
(devir azaltma + topluluk adayları) sonrası Tur 3'te **6/6 kriterle KABUL** —
final spek değişmedi: **Donchian 20/10**. Birleşik OOS (5 sembol, 2013–2026):
Sharpe **1.76**, yıllık %138, maks düşüş -%65 (satın-al-tut: 1.36 / %126 / -%87);
son 24 ay birleşik **+%26,1**.

Sembol bazında (sabit spek, 20 bps):

| Sembol | OOS Sharpe | İsabet | Son 24 ay (strateji / al-tut) |
|---|---|---|---|
| BTCUSDT | 1.53 | %54 | +%35,3 / +%10,9 |
| ETHUSDT | 0.97 | %49 | -%19,2 / -%43,4 |
| BNBUSDT | 1.15 | %50 | -%32,8 / +%6,8 |
| XRPUSDT | 1.14 | %47 | +%238,4 / +%158,0 |
| ADAUSDT | 1.02 | %48 | -%23,2 / -%49,1 |

**Dürüst okuma:** kuralın gücü *portföy* düzeyindedir (5 sembol ortalaması son 24
ayda +%26 iken BNB tek başına -%33). Tek sembolde, özellikle yatay piyasada, aylarca
süren zarar serileri bu kuralın **beklenen** davranışıdır. Doğrulanmamış sembollerde
(hisse, altın, küçük altcoinler) performans garanti edilmez. Ayrıca K6/H8'in yakın
pencereye bakması tazelik yanlılığı taşır — bu yüzden K6 tek başına değil, 13 yıllık
walk-forward kriterleriyle (K1–K5) birlikte aranır.

## Koşu 3 (2026-07-08) — "Evrensellik" turnuvası: tek kural her sembolde çalışır mı?

Kullanıcı isteği: BTC'de de, NVDA'da da, ASELSAN'da da çalışacak **genel** bir kural.
Dürüst ön not: literatürde "her sembolde her zaman kârlı" kural yoktur; ulaşılabilir
hedef, birçok varlık sınıfında **ortalamada** işleyen tek kuraldır (Faber 2007;
Hurst-Ooi-Pedersen 2017 — bkz. LITERATUR §3b).

**Tasarım:** 10 literatür kuralı (kısa/orta/uzun pencere aileleri), sabit
parametrelerle, sembol başına HİÇBİR uyarlama yapılmadan **491 sembole** uygulandı:
486 S&P 500 hissesi (günlük, 2013-02 → 2018-02; plotly/datasets `all_stocks_5yr`)
+ 5 kripto (13 yıl, Coin Metrics). 20 bps maliyet, +1 gün gecikme. BIST için bu
ortamdan erişilebilir veri kaynağı yoktur (Binance/Yahoo/Stooq/FRED/WSJ ağ
politikasında engelli) — ASELSAN sınaması kullanıcı tarafında Strategy Tester veya
CSV ihracıyla yapılmalıdır.

**Sonuç (sınıf bazında medyan net Sharpe | pozitif sembol %):**

| Kural | Hisseler | Kripto | En kötü sınıf |
|---|---|---|---|
| **SMA 50/200 (altın kesişim)** | **0.4 \| %78** | 0.8 \| %100 | **0.4** ← kazanan |
| fiyat/SMA-200 (Faber) | 0.3 \| %69 | 0.8 \| %100 | 0.3 |
| TSMOM-90 | 0.3 \| %69 | 1.0 \| %100 | 0.3 |
| Donchian 100/50 | 0.2 \| %71 | 1.2 \| %100 | 0.2 |
| **Donchian 20/10 (kripto şampiyonu)** | 0.1 \| %54 | **1.4 \| %100** | 0.1 |
| RSI>50 | -0.1 \| %43 | 1.4 \| %100 | -0.1 |

Ana bulgular:
- **Pencere uzadıkça kural evrenselleşir**: tekil hisselerde kısa pencereler
  (Donchian 20/10, RSI) testere zararına boğulur; 50/200 ve 200-gün kuralları
  sembollerin ~%70-78'inde pozitif kalır (Wilcox-Crittenden 2005 ile uyumlu).
- **Kriptoda kısa pencereler üstün** — Koşu 1-2'nin Donchian 20/10 sonucu geçerli;
  ama bu kural hisselere taşınmaz. "Tüm sembollerde tek kural" isteniyorsa bedeli,
  kriptodaki keskinlikten vazgeçmektir.
- **Boğa piyasasında satın-al-tut'u geçmek nadir**: 2013-2018 hisse penceresinde
  50/200 bile sembollerin yalnız %15'inde al-tut Sharpe'ını geçti; buna karşılık
  %65'inde maks düşüşü küçülttü. Uzun-pencere trend kuralının değeri (Faber'in ana
  bulgusu) ayı piyasalarında ortaya çıkar — test penceremizde 2008/2022 tipi bir
  çöküş yoktur, bu pencere kuralın lehine değil aleyhinedir.
- **NVDA (2013-2018) özelinde 10 kuralın 10'u da kârlı**: altın kesişim +%1.191
  (Sharpe 2.04), Donchian 20/10 +%312. Hiçbiri al-tut'u (Sharpe 2.19) geçemedi —
  10× yükselen hissede al-tut'un rakibi yoktur.

**Karar — iki mod:**
- `final_indikator.al_sat_sinyali` (Donchian 20/10): **kripto** için.
- `final_indikator.evrensel_al_sat_sinyali` (SMA 50/200): **her sembol** için
  ("en kötü sınıfta en iyi" ölçütünün kazananı). Pine: `alsat_evrensel_*.pine`.

**Sınırlılıklar:** hisse penceresi 5 yıl ve tek rejim (boğa); 10 kural arasından
seçim hafif çoklu-test etkisi taşır (10 deneme, tablo tam raporlandı); BIST/altın
doğrulanmadı; tekil hisse trend takibi portföy halinde (çok sembolde aynı anda)
uygulandığında anlamlıdır, tek hissede varyans yüksektir.

## Meta post-mortem (aracın kendisine uygulanan Reviewer 2)

Döngünün ilk sürümünde iki kusur koşu sırasında yakalandı ve düzeltildi:

1. **DSR sabitlenmesi:** denemeler-arası Sharpe dağılımı bilinmediğinde kullanılan
   "gözlenen SR'nin yarısı" varsayımı DSR'yi yapısal olarak ~0.5'e kilitliyordu.
   Düzeltme: Bailey-LdP (2014)'ün öngördüğü gibi std artık **aday tablosundan ampirik**
   hesaplanıyor.
2. **Döngü durağanlığı:** hakem önerileri konfigürasyonu değiştirmez hâle gelince turlar
   birebir tekrarlanıyordu. Düzeltme: durağanlık algılanınca henüz denenmemiş düzeltmeye
   (vol filtresi → topluluk → maliyet artırma) tırmanılır; çare kalmadıysa döngü erken
   ve gerekçeli biter.

## Sınırlılıklar (dürüstlük bölümü)

- **-%65 maks düşüş** kabul kriterini geçse de mutlak olarak çok derindir; kural düşüş
  *azaltır*, düşüşten *korumaz*. Pozisyon boyutlandırma/vol hedefleme kullanıcıya kalır.
- Veri **kapanış tabanlıdır** (Coin Metrics `PriceUSD`); gün içi yüksek/düşük
  kullanılmamıştır. Gerçek Donchian klasiği yüksek/düşükle tanımlanır; kapanış çeşidi
  biraz daha yavaş tetiklenir.
- İki varlık (BTC, ETH) sınandı; başka varlıklara genellemesi test edilmedi
  (`--sembol` ile genişletilebilir).
- 20 bps maliyet varsayımı spot piyasa için makuldür; yüksek kayma koşullarında K3
  stres sonuçlarına (2×/4×) bakınız.
- H1 uyarısı kalıcıdır: sinyali gördükten sonra **ertesi günün fiyatından** işlem
  yapabildiğinizi varsayar; aynı-gün kapanışta işlem yaptığını iddia eden her backtest
  bu kuralın Sharpe'ını yapay olarak ~2 katına çıkarır.
- Geçmiş performans gelecek getirinin garantisi değildir. Bu rapor araştırma çıktısıdır,
  yatırım tavsiyesi değildir.

## Yeniden üretme

```bash
pip install -r requirements.txt
python -m alsat --sembol BTCUSDT ETHUSDT -o alsat/alsat_rapor.xlsx
# ağ yoksa: python -m alsat --sembol BTCUSDT --csv BTCUSDT=veri.csv
```

Veri önbelleği `data/alsat_cache/` altına iner (git'e girmez); kaynak zinciri
Binance → Crypto.com → Coin Metrics (GitHub) sırasıyla denenir.
