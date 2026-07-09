# 📈 AlSat — Literatür Temelli Al-Sat İndikatörü Laboratuvarı

Akademik literatürden türetilmiş aday göstergeleri (bkz. [LITERATUR.md](LITERATUR.md))
gerçek veriyle **walk-forward** sınar, sonucu **Reviewer 2** gibi düşmanca denetler,
post-mortem çıkarır, düzeltir ve **kabul kriterleri sağlanana kadar** (en fazla 5 tur)
bu döngüyü işletir. PaperForge (`app/`) kodundan tamamen bağımsızdır; megastat gibi
tek komutla çalışır.

Son koşunun sonucu ve tur tur post-mortem kayıtları: **[RAPOR.md](RAPOR.md)** ·
Kabul edilen final indikatör (bağımsız dosya): **[final_indikator.py](final_indikator.py)**

## Çalıştırma

```bash
python -m alsat                                  # BTCUSDT + ETHUSDT, 5 tur, 20 bps
python -m alsat --sembol BTCUSDT SOLUSDT --tur 3 --maliyet 30 -o rapor.xlsx
python -m alsat --sembol BIST100=X --csv "BIST100=X=bist.csv"   # herhangi bir OHLCV CSV
```

Veri, anahtarsız kaynak zincirinden çekilir (Binance → Crypto.com → Coin Metrics/GitHub)
ve `data/alsat_cache/` altına önbelleklenir. Çıktı: çok sayfalı Excel raporu + konsol özeti.

## Döngü nasıl çalışır?

1. **Aday üretimi** — 8 literatür-kaynaklı kural ailesi × parametre ızgarası
   (SMA/EMA kesişimi, fiyat/SMA, TSMOM, Donchian kırılımı, RSI, MACD, Bollinger).
2. **Sınama** — genişleyen pencereli walk-forward (eğitim ≥ 3 yıl, test = takvim yılı);
   her yılın kuralı yalnız o yıldan önceki veriyle seçilir; sinyaller +1 gün gecikmeli,
   işlem maliyeti + kayma her pozisyon değişiminde düşülür. Raporlanan performans tek
   bir kuralın değil, **seçim prosedürünün** örneklem-dışı performansıdır.
3. **Reviewer 2 (hakem.py)** — sekiz deterministik düşmanca denetim:
   H1 ileri-bakış/gecikme duyarlılığı, H2 parametre hassasiyeti, H3 maliyet stresi
   (2×/4×), H4 rejim/varlık sağlamlığı, H5 veri madenciliği (Deflated Sharpe Ratio),
   H6 IS→OOS bozulması, H7 satın-al-tut kıyası, H8 güncel rejim (son 24 ay).
4. **Post-mortem + düzeltme** — her eleştiri makine-eylemli bir öneri taşır
   (sadeleştir, devir azalt, volatilite filtresi, topluluk/ensemble, maliyet artır);
   öneriler bir sonraki turun aday üretimine uygulanır. Döngü durağanlaşırsa henüz
   denenmemiş düzeltmeye tırmanır, çare kalmadıysa erken ve gerekçeli durur.
5. **Kabul kriterleri (K1–K6)** — OOS net Sharpe > 0.5 (her sembolde > 0), DSR ≥ 0.95,
   2× maliyette pozitif getiri, satın-al-tut'tan belirgin düşük maks düşüş, hakem
   engeli olmaması, son 24 ayda mutlak kazanç veya satın-al-tut'a üstünlük.
   Sağlanamazsa en iyi aday **"kabul edilmedi"** etiketiyle raporlanır —
   bu bir hata değil, dürüst bilimsel sonuçtur.

## Dosyalar

| Dosya | İçerik |
|---|---|
| `veri.py` | Anahtarsız veri zinciri + CSV yükleyici + disk önbelleği |
| `gostergeler.py` | Kural aileleri (her biri literatür atıflı) + vol hedefi + topluluk |
| `sinama.py` | Nedensel backtest (shift(1)), maliyet, walk-forward dilimleri |
| `olcutler.py` | Sharpe/Sortino/düşüş + DSR (Bailey-LdP 2014) + blok bootstrap p |
| `hakem.py` | Reviewer 2: H1–H7 denetimleri, makine-eylemli öneriler |
| `dongu.py` | Tur motoru: aday → sınama → hakem → post-mortem → düzeltme |
| `rapor.py` | Çok sayfalı Excel + konsol özeti |
| `final_indikator.py` | Kabul edilen kural, tek başına kopyalanabilir |
| `ogrenme.py` | ML katmanı (havuzlanmış GBM, sızıntısız walk-forward) — Koşu 4'te basit kurallara yenildi, kayıt için durur |
| `pine/` | TradingView Pine (v6): Donchian 20/10 (kripto) + Evrensel 50/200 (her sembol), indikatör + strateji |

## Uyarı

Bu araç bir **araştırma laboratuvarıdır**; çıktıları yatırım tavsiyesi değildir.
Geçmiş performans gelecek getirinin garantisi değildir; en sağlam görünen kural bile
örneklem dışında zayıflayabilir (bkz. LITERATUR.md'deki Hudson-Urquhart ihtiyatı).
