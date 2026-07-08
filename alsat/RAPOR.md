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
