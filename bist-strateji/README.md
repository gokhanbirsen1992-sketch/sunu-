# 📈 BIST HODL-Beater — Al/Sat Strateji İndikatörü

BIST (Borsa İstanbul) için, **günlük ve haftalık grafikte** çalışan, long/flat
al-sat stratejisi. Grafiğin köşesindeki canlı performans tablosu, seçtiğin
parametrelerle stratejinin geçmişte ne yaptığını **HODL (al-ve-tut)** ile
karşılaştırır — parametreleri optimize ettikçe tablo ve işlem listesi anında
güncellenir.

## İki mod

### 1) Rejim Filtresi — ana mod (3 aşamalı sağlamlık testini geçti)

> Varsayılan pozisyon **LONG**. Yalnızca **çifte ayı teyidinde** çıkar:
> `kapanış < SMA(131 gün) × 0.97` **VE** `284 günlük momentum < 0`.
> Geri giriş hızlı: `kapanış > SMA` **VEYA** `momentum > 0`. 10 yılda ~6-8 işlem.

Literatür: Faber (2007) trend filtresi + Antonacci (2014) mutlak momentum +
Zakamulin histerezis bandı + Moskowitz-Ooi-Pedersen (2012) zaman-serisi momentumu.

Doğrulama özeti (ayrıntılar `sonuclar/SONUCLAR.md`):

| Aşama (sentetik BIST senaryoları) | CAGR farkı | HODL'u geçme | MaksDD farkı |
|---|---|---|---|
| Out-of-sample (15 görülmemiş senaryo) | **+1.54 puan/yıl** | **%66.7** | **-18.1 puan** |
| Nihai onay (el değmemiş 15 senaryo) | +0.18 puan/yıl | %60 | -5.9 puan |

⚠ **Endeks profili için doğrulandı** (XU100 ve benzeri geniş sepetler).
Tekil hisselerde getiri avantajı doğrulanamadı (yalnızca düşüş koruması).
Günlük grafik hafif önde; haftalık da geçerli.

### 2) Zirve İz Stop — tepeye yakın satış (3 aşamalı testi geçti)

> SAT: kapanış, pozisyon **zirvesinin %10 altına** inince — satış her zaman
> tepeye yakın olur, dipte değil. AL: kapanış > SMA(100g) veya momentum > 0
> veya fiyat çıkış fiyatını aşarsa (breakeven). 10 yılda ~15-19 işlem.
> OOS skor +1.95, nihai onay +0.78 (endeks profili). Rejim filtresinden daha
> sık işlem yapar ama satış noktaları psikolojik olarak çok daha rahattır.

### 3) Komposit Puanlama — deneysel mod

6 indikatör oyu (Supertrend, EMA kesişimi, MACD, RSI, Donchian, DMI) +
Chandelier Exit + Elder haftalık teyidi. Eğitimde parlak görünüp **örneklem
dışında HODL'a yenildiği için** yalnızca araştırma/eğitim amaçlı bırakıldı —
tabloda "deneysel" olarak işaretlenir. Aşırı uyumun (overfitting) ders niteliğinde
bir örneği olarak depoda tutuluyor.

## TradingView'e kurulum

1. TradingView'de bir BIST sembolü aç (ör. `BIST:XU100`).
2. Alt paneldeki **Pine Editor**'ü aç.
3. `BIST_HODL_Beater.pine` içeriğini yapıştır → **Add to chart**.
4. Zaman dilimini **1G** veya **1H** seç. Tabloda Net Kâr, HODL, Alpha, CAGR,
   Maks. Düşüş, İşlem Sayısı, Kazanma Oranı, Kâr Faktörü ve "HODL'a karşı
   GEÇTİ/geride" satırlarını gör; **Strategy Tester** işlem işlem döküm verir.
5. ⚙ ayarlardan parametre değiştir — tablo her değişiklikte yeniden hesaplanır.
   Periyotlar **işlem günü** cinsindendir; haftalık grafikte otomatik ölçeklenir.
6. `Alerts` menüsünden "BIST HODL-Beater AL / SAT" koşullarına alarm kur —
   sinyaller telefonuna bildirim olarak gelir.

## Parametre optimizasyonu

- TradingView'de elle: ⚙ ayarlar → tablo canlı güncellenir.
- Sistematik: bu klasördeki Python düzeneği (aşağıda). Doğrulanmış plato:
  `sma_gun` 131-150, `mom_gun` 284-315, `band` %2.25-3.75 — bu aralık dışına
  çıkmak (özellikle `mom_gun`'ı kısaltmak) test sonuçlarına göre zarar verir.

```bash
pip install pandas numpy pytest
cd bist-strateji
python3 -m pytest backtest/  # motor doğruluk testleri

# Gerçek veriyle (TradingView → Export chart data... → CSV):
python3 - <<'PY'
from backtest.veri import csv_yukle
from backtest.optimize import kos
df = csv_yukle("XU100_gunluk.csv")
r = kos("rejim_filtre", {"sma_gun":131, "mom_gun":284, "band_yuzde":3.0, "be_giris":0}, df, 252.0)
print(f"Net %{r.net_kar_yuzde:.0f}  HODL %{r.hodl_yuzde:.0f}  İşlem {r.islem_sayisi}  "
      f"Kazanma %{r.kazanma_orani:.0f}  MaksDD %{r.maks_dusus:.0f} (HODL %{r.hodl_maks_dusus:.0f})")
PY
```

Izgara arama: `backtest.optimize.grid_ara(aile, izgara)` — skor formülü:
**medyan yıllık CAGR farkı − 0.25 × medyan maksimum düşüş farkı**; işlem
üretmeyen "hep long" çözümleri otomatik elenir.

## Doğrulama protokolü

Bu ortamdan gerçek BIST verisi çekilemediği için strateji, **BIST karakterine
kalibre edilmiş** rejim-değişimli sentetik senaryolarda test edildi (medyan
yıllık getiri %29, medyan maks. düşüş %45, boğa içi şok düzeltmeleri —
Mart/Kasım 2021, Temmuz 2023 tarzı):

1. **Eğitim** (seed 0-19): 10 aile × ~1000 kombinasyon ızgara arama.
2. **İnce ayar**: en iyi ailelerde plato analizi (tek nokta zirvesi = overfit reddi).
3. **Out-of-sample** (seed 100-114): düşmanca doğrulama ajanları — 1. turnuvanın
   4 parlak adayının 4'ü de burada elendi.
4. **Nihai onay** (seed 200-214): hiçbir optimizasyonda kullanılmamış senaryolar.

Motor 10+ birim testiyle doğrulandı (Wilder RSI/ATR/ADX değerleri, sonraki bar
açılışı dolumu, komisyon muhasebesi, Pine ile stop paritesi). Komisyon her
bacakta %0.1. Sinyal bar kapanışında üretilir, emir **bir sonraki barın
açılışında** dolar — TradingView `strategy()` ile birebir aynı model.

## Dürüst uyarılar

- Sentetik senaryolar sağlamlık testidir, gelecek tahmini değildir. Gerçek
  geçmiş performansı TradingView tablosu gerçek BIST verisiyle gösterir.
- Kesintisiz güçlü boğada long/flat sistemin ana katkısı getiri değil,
  **büyük düşüşleri ciddi azaltmaktır**; getiri farkı ayı/yatay dönemler
  içeren uzun periyotlarda ortaya çıkar.
- Tek sembolün tek dönemine göre parametre inceltme = aşırı uyum tuzağı.
- Bu bir yatırım tavsiyesi değildir.
