# BTC/USDT Sinyal Botu

Crypto.com Exchange üzerinden BTC/USDT (veya istediğin başka bir USDT paritesi) parametrelerini takip eden, **AL/SAT/BEKLE** sinyalleri üreten ve önerilen stop-loss / take-profit / pozisyon büyüklüğünü hesaplayan terminal tabanlı bir araç.

## ⚠️ Uyarı

**Bu bot yatırım tavsiyesi değildir, sadece eğitim amaçlıdır.**
- Hiçbir gerçek emir verilmez. Sadece public veriyi okur ve önerileri ekrana yazar.
- API anahtarı veya cüzdan bilgisi gerektirmez.
- Geçmiş performans gelecekteki sonuçların garantisi değildir. Kararlar tamamen kullanıcının sorumluluğundadır.

## Özellikler

- 📊 **3 hazır strateji**: RSI + EMA crossover, MA crossover, Bollinger + RSI — `config.yaml`'dan seçilebilir.
- 📈 **Günlük (1D) zaman dilimi** üzerinde çalışır (config'den değiştirilebilir).
- ⏱️ **30 saniyede bir** anlık fiyatı çeker, sinyali yeniler.
- 🎯 **Risk yönetimi**: ATR tabanlı stop-loss/take-profit, risk-yüzdesi tabanlı pozisyon büyüklüğü önerisi.
- 🔁 **Backtest**: Geçmiş 300 mum üzerinde stratejiyi simüle eder; kazanma oranı, getiri, max drawdown raporu.
- 🎨 **Renkli terminal arayüzü** (Rich): canlı yenilenen panel + sinyal değişim logları.

## Kurulum

```bash
git clone https://github.com/gokhanbirsen1992-sketch/sunu-.git
cd sunu-
pip install -r requirements.txt
```

Python 3.10+ gereklidir.

## Kullanım

### Canlı izleme

```bash
python -m src.main monitor
```

Çıktı örneği:

```
╭───────────────────── BTC/USDT Sinyal Botu — Crypto.com ─────────────────────╮
│      Sembol  BTC_USDT   (1D)                                                │
│    Strateji  rsi_ma                                                         │
│       Fiyat  80,283.38 USDT                                                 │
│ Göstergeler  rsi=58.4  ema_50=78,102.55  ema_200=72,914.30  atr=1904.96     │
│      Sinyal  BUY                                                            │
│   Stop-Loss  76,473.46                                                      │
│ Take-Profit  87,903.22                                                      │
│ Önerilen…    156.21 USDT                                                    │
│       Sebep  Yükseliş trendi (EMA50>EMA200) + RSI=28.4 aşırı satım          │
╰──────────── Yatırım tavsiyesi değildir. Sadece eğitim amaçlıdır. ───────────╯
```

`Ctrl+C` ile durdurulur.

### Tek seferlik anlık sinyal

```bash
python -m src.main signal
```

### Backtest

```bash
python -m src.main backtest --strategy rsi_ma
python -m src.main backtest --strategy ma_crossover --candles 500
python -m src.main backtest --strategy bb_rsi --fee-pct 0.0015
```

### Strateji veya sembol değiştirme

CLI üzerinden geçici geçersiz kılma:

```bash
python -m src.main monitor --strategy ma_crossover --symbol ETH_USDT
```

Veya `config.yaml` dosyasını düzenle:

```yaml
strategy:
  active: bb_rsi      # rsi_ma | ma_crossover | bb_rsi
exchange:
  symbol: BTC_USDT    # ETH_USDT, SOL_USDT vb. de çalışır
  timeframe: 1D       # 1m,5m,15m,30m,1h,4h,6h,12h,1D,7D,14D,1M
  poll_interval_sec: 30
```

## Stratejiler

| Strateji | Mantık |
|---|---|
| `rsi_ma` | Yükseliş trendinde (EMA50 > EMA200) RSI < 30 → AL. Düşüş trendinde RSI > 70 → SAT. |
| `ma_crossover` | EMA20 yukarı doğru EMA50'yi keserse AL; aşağı keserse SAT. |
| `bb_rsi` | Fiyat alt Bollinger bandı altına düşer ve RSI < 30 → AL. Üst banda çıkıp RSI > 70 → SAT. |

## Risk Yönetimi

`config.yaml` içindeki `risk` bölümü:

```yaml
risk:
  equity_usdt: 1000      # toplam sermaye (varsayım)
  risk_pct: 0.01         # işlem başına risk %1
  atr_period: 14
  atr_sl_mult: 2.0       # stop-loss = entry - 2*ATR
  atr_tp_mult: 4.0       # take-profit = entry + 4*ATR  → R:R 1:2
```

## Test

```bash
pip install -r requirements.txt
python -m pytest tests/ -v
```

## Mimari

```
src/
├── exchange.py       # Crypto.com public REST client (httpx)
├── indicators.py     # SMA, EMA, RSI, Bollinger, ATR
├── signal.py         # Signal dataclass
├── risk.py           # SL/TP ve pozisyon büyüklüğü hesabı
├── strategies/       # Strateji sınıfları (registry pattern)
├── backtest.py       # Tek pozisyon, SL/TP destekli backtester
├── monitor.py        # Rich Live ile canlı tablo
└── main.py           # click CLI
```

## Sıkça Sorulanlar

**Gerçek emir verecek mi?**
Hayır. Bu bot yalnızca public okuma yapar — API anahtarı kullanmaz. Gerçek emir desteği kasıtlı olarak eklenmemiştir.

**Başka borsa eklenebilir mi?**
Evet. `src/exchange.py`'a benzer bir Binance/CCXT istemcisi yazıp `Exchange` arayüzünü taklit etmek yeterli.

**Yeni strateji nasıl eklerim?**
1. `src/strategies/` altında `Strategy` sınıfını miras alan bir dosya oluştur.
2. `src/strategies/__init__.py` içindeki `STRATEGY_REGISTRY`'ye ekle.
3. `config.yaml`'a parametrelerini ekle.

## Lisans

MIT
