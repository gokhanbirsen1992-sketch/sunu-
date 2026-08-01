# 📈 BIST HODL-Beater — Al/Sat Strateji İndikatörü

BIST (Borsa İstanbul) hisseleri ve XU100 endeksi için, **günlük ve haftalık grafikte**
çalışan, literatürdeki kanıtlanmış tekniklerin oylamasıyla karar veren **long/flat**
al-sat stratejisi. Grafiğin köşesindeki canlı performans tablosu, seçtiğin
parametrelerle stratejinin geçmişte ne yaptığını **HODL (al-ve-tut)** ile
karşılaştırır — parametreleri değiştirdikçe tablo anında güncellenir.

## Bileşenler (literatür)

| Oy | Bileşen | Kaynak |
|----|---------|--------|
| 1 | Supertrend yönü yukarı | Olivier Seban |
| 2 | Hızlı EMA > Yavaş EMA | Brock, Lakonishok & LeBaron (1992), *Journal of Finance* |
| 3 | MACD histogram > 0 | Gerald Appel |
| 4 | RSI > eşik (momentum rejimi) | J. Welles Wilder (1978) |
| 5 | Fiyat Donchian orta hattının üstünde | Richard Donchian / Turtle Traders |
| 6 | +DI > −DI (yön hakimiyeti) | J. Welles Wilder (1978) |
| — | Chandelier Exit iz süren stop | Chuck LeBeau |
| — | Haftalık trend teyidi (isteğe bağlı) | Alexander Elder, *Üçlü Ekran* |

**Karar kuralı:** 6 bileşen oy verir → puan **giriş eşiğine** ulaşınca **AL**,
**çıkış eşiğine** düşünce veya iz süren stop kırılınca **SAT**. Açığa satış yok
(BIST gerçeğine uygun); pozisyon yokken nakitte bekler.

## TradingView'e kurulum

1. TradingView'de bir BIST sembolü aç (ör. `BIST:XU100`, `BIST:THYAO`).
2. Alt paneldeki **Pine Editor**'ü aç.
3. `BIST_HODL_Beater.pine` dosyasının tüm içeriğini yapıştır → **Add to chart**.
4. Grafiğe gelen tabloda Net Kâr, HODL, Alpha, CAGR, Maks. Düşüş, İşlem Sayısı,
   Kazanma Oranı, Kâr Faktörü satırlarını gör. **Strategy Tester** sekmesi
   işlem işlem dökümü verir.
5. ⚙ ayarlardan parametreleri değiştir; tablo ve işlem listesi her değişiklikte
   yeniden hesaplanır. Zaman dilimini **1G** (günlük) veya **1H** (haftalık) seç.

> ⏰ **Uyarılar:** `Alerts` menüsünden "BIST HODL-Beater AL / SAT" koşullarına
> alarm kurarak sinyalleri telefonuna bildirim olarak alabilirsin.

## Parametre optimizasyonu nasıl yapılır?

- TradingView'de ⚙ ayarlardan tek tek deneyebilirsin (tablo canlı güncellenir).
- Sistematik arama için bu klasördeki Python düzeneğini kullan:

```bash
pip install pandas numpy pytest
cd bist-strateji

# Gerçek veriyle: TradingView'den "Export chart data..." ile CSV indir
python3 - <<'PY'
from backtest.veri import csv_yukle
from backtest.optimize import kos
df = csv_yukle("XU100_gunluk.csv")
r = kos("komposit", {"st_n":10,"st_mult":3.0,"ema_hizli":20,"ema_yavas":100,
                     "giris_esik":5,"cikis_esik":2,"chand_mult":3.0,"dc_n":20}, df, 252.0)
print(f"Net %{r.net_kar_yuzde:.0f}  HODL %{r.hodl_yuzde:.0f}  "
      f"İşlem {r.islem_sayisi}  Kazanma %{r.kazanma_orani:.0f}  MaksDD %{r.maks_dusus:.0f}")
PY
```

Izgara arama: `backtest.optimize.grid_ara(aile, izgara_sözlüğü)` — skor,
**yıllık getiri farkı (CAGR − HODL CAGR) − 0.25 × maks. düşüş farkı** formülüyle
hesaplanır; işlem üretmeyen "hep long" çözümleri otomatik elenir.

## Doğrulama protokolü (bu depoda yapılan)

Gerçek zamanlı BIST verisi bu çalışma ortamında dışarıdan çekilemediği için
strateji, **BIST karakterine kalibre edilmiş** (TL bazlı yüksek nominal getiri,
%20-45 aralığında ayı fazları, sert tek gün düşüşleri, uzun testere dönemleri)
rejim-değişimli sentetik senaryolarda test edildi:

- **Eğitim:** 10 senaryo × (günlük + haftalık) ızgara arama — 6 strateji ailesi
  (Supertrend+ADX, EMA+MACD, Donchian/Turtle, KAMA+Momentum, RSI ortalamaya
  dönüş, Komposit oylama) yarıştı.
- **Doğrulama:** Kazanan parametreler, eğitimde hiç görülmemiş 15 senaryoda
  (endeks + tekil hisse profili) out-of-sample test edildi.
- Komisyon her işlem bacağında %0.1 olarak dahil edildi.
- Motorun kendisi 10+ birim testiyle (Wilder RSI/ATR/ADX değerleri, sonraki bar
  açılışı dolumu, komisyon muhasebesi, bar içi stop) doğrulandı.

Sonuç özeti için `sonuclar/` klasörüne bak. **Not:** Sentetik senaryolar bir
gelecek tahmini değil, sağlamlık testidir. Kesin geçmiş performansı TradingView
tablosu gerçek BIST verisiyle gösterir.

## Dürüst uyarılar

- Geçmiş performans geleceği garanti etmez; sonuçlar sembole ve döneme göre değişir.
- Güçlü, kesintisiz boğa piyasasında long/flat bir sistemin HODL'u **getiride**
  geçmesi zordur; bu stratejinin ana avantajı **düşüşleri ciddi azaltarak**
  riske göre getiriyi (ve çoğu senaryoda mutlak getiriyi) iyileştirmesidir.
- Aşırı optimizasyon (overfitting) tuzağına dikkat: parametreyi tek sembolün
  tek dönemine göre inceltme; komşu değerlerde de iyi çalışan ayarları seç.
- Bu bir yatırım tavsiyesi değildir.
