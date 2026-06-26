# Modül 12 — Zaman Serisi Analizi

> **Hedef:** Zamana bağlı veriyi (fiyat, hacim, talep) modellemek ve tahmin
> etmek. Trading'in doğal dilidir. Sıradan ML'in kurallarının çoğu burada
> değişir — çünkü gözlemler **bağımsız değildir**.

---

## 1. Zaman serisini özel kılan ne?

- **Otokorelasyon:** Bugünkü değer dünküne bağlı (bağımsızlık varsayımı çöker).
- **Sıra önemli:** Veriyi karıştıramazsın (shuffle = sızıntı, Modül 08).
- **Trend ve mevsimsellik:** Sistematik desenler.
- **Geleceği bilemezsin:** Doğrulama mutlaka ileri yönlü (walk-forward) olmalı.

---

## 2. Bir zaman serisinin bileşenleri

$$Y_t = \text{Trend}_t + \text{Mevsimsellik}_t + \text{Döngü}_t + \text{Gürültü}_t$$

- **Trend:** Uzun vadeli yön.
- **Mevsimsellik:** Sabit periyotlu tekrar (günlük, haftalık, yıllık).
- **Döngü:** Periyodu değişken dalgalanma (ekonomik döngüler).
- **Artık (gürültü):** Açıklanamayan.

`statsmodels.tsa.seasonal_decompose` veya STL ile ayrıştırılır.

---

## 3. Durağanlık (Stationarity) — en kritik kavram

Bir seri **durağansa**: ortalaması, varyansı ve otokorelasyonu zamanla
değişmez. Klasik modeller (ARIMA) **durağanlık ister.**

Fiyatlar durağan **değildir** (trend var). Ama **getiriler/farklar** genelde
durağandır → bu yüzden fiyat yerine getiri modellenir.

- **Test:** ADF (Augmented Dickey-Fuller) — p<0.05 ise durağan. KPSS (tersi).
- **Durağanlaştırma:** Fark alma (differencing, `diff()`), log dönüşümü,
  trend/mevsim çıkarma.

```python
from statsmodels.tsa.stattools import adfuller
fiyat = df["close"]
print("Fiyat ADF p:", adfuller(fiyat)[1])              # büyük → durağan değil
print("Getiri ADF p:", adfuller(fiyat.pct_change().dropna())[1])  # küçük → durağan
```

---

## 4. ACF ve PACF — model derecesi seçimi

- **ACF (otokorelasyon):** Y_t ile Y_{t−k} arası korelasyon (MA derecesi q için).
- **PACF (kısmi otokorelasyon):** Aradaki etkileri çıkarınca kalan ilişki
  (AR derecesi p için).

Bu iki grafiğin kesilme/sönme deseni ARIMA(p,d,q) derecelerini önerir.

---

## 5. Klasik modeller: AR, MA, ARIMA, SARIMA

- **AR(p) — Otoregresif:** Bugün = geçmiş değerlerin doğrusal kombinasyonu.
  $$Y_t = c + \phi_1 Y_{t-1} + \dots + \phi_p Y_{t-p} + \varepsilon_t$$
- **MA(q) — Hareketli Ortalama:** Bugün = geçmiş **hataların** kombinasyonu.
- **ARIMA(p,d,q):** AR + MA + **d kez fark alma** (durağanlaştırma). En yaygın klasik.
- **SARIMA:** ARIMA + mevsimsellik.
- **SARIMAX:** + dışsal değişkenler (X — örn. hacim, makro veri).

```python
from statsmodels.tsa.arima.model import ARIMA
model = ARIMA(getiri, order=(1, 0, 1)).fit()   # (p,d,q)
print(model.summary())
tahmin = model.forecast(steps=5)               # 5 adım ileri tahmin

# Otomatik derece seçimi:
# from pmdarima import auto_arima; auto_arima(getiri, seasonal=False)
```

---

## 6. Oynaklık modelleme: ARCH / GARCH — finansın kalbi

Getirilerin ortalamasını tahmin etmek zordur (piyasa neredeyse rastgele yürür).
Ama **oynaklığı (volatilite) tahmin etmek mümkündür** çünkü oynaklık **kümelenir**:
sakin günleri sakin, çalkantılı günleri çalkantılı izler.

- **ARCH:** Bugünkü varyans = geçmiş şokların karelerine bağlı.
- **GARCH(1,1):** En yaygın. Varyans = sabit + dünkü şok² + dünkü varyans.

```python
from arch import arch_model
getiri_pct = df["close"].pct_change().dropna() * 100
am = arch_model(getiri_pct, vol="GARCH", p=1, q=1, dist="t")  # t: şişman kuyruk
res = am.fit(disp="off")
print(res.summary())
vol_tahmin = res.forecast(horizon=5).variance   # gelecek 5 gün oynaklık tahmini
```

> 💡 Risk yönetimi, opsiyon fiyatlama, VaR (riske maruz değer) ve pozisyon
> büyüklüğü hesabı GARCH oynaklık tahminine dayanır. Bu repodaki botun
> ATR'si (Modül 16) bunun basit bir akrabasıdır.

---

## 7. Modern yaklaşımlar

- **Prophet (Meta):** Trend + mevsimsellik + tatil etkilerini otomatik ayırır.
  İş tahminlerinde (talep, trafik) pratik, az ayar ister. Yüksek frekanslı
  finansal getiri için ideal değildir.
- **Üstel düzleştirme (ETS / Holt-Winters):** Hafif, sağlam, mevsimsel tahmin.
- **State space / Kalman filtresi:** Gizli durumu zamanla güncelleme; gürültülü
  sinyalden trend çıkarma.
- **ML tabanlı (kayan pencere özellikleri + boosting):** Geçmiş değerleri,
  hareketli ortalamaları, takvim özelliklerini "feature" yapıp XGBoost/LightGBM
  (Modül 10) ile tahmin. Çok popüler ve güçlü — **sızıntıya dikkat**.
- **Derin öğrenme:** LSTM, GRU, Temporal Fusion Transformer, N-BEATS, PatchTST.
  Çok veri ve dikkatli doğrulama ister; her zaman klasiği yenmez (Modül 15).

---

## 8. Tahmin doğrulama — zaman serisine özel

- **ASLA shuffle etme.** Geçmişle eğit, gelecekle test et.
- **Walk-forward / TimeSeriesSplit** (Modül 08).
- **Backtest** ≠ canlı. İşlem maliyeti, slippage, likidite, look-ahead bias'ı
  hesaba kat. (Bu repodaki `src/backtest.py` bunu örnekler.)
- **Naive baseline:** "Yarın = bugün" (random walk). Çoğu karmaşık model bunu
  yenmekte zorlanır — finansal serilerin ayık gerçeği budur.
- **Metrikler:** MAE, RMSE, MAPE (tahmin); yön doğruluğu (directional accuracy),
  Sharpe oranı, max drawdown (trading).

---

## 9. Tuzaklar

- **Sahte regresyon (spurious):** İki trendli durağan-olmayan seri "korele" görünür
  ama anlamsızdır. Önce durağanlaştır.
- **Look-ahead bias:** Tahmin anında olmayan bilgiyi kullanmak. En sık ölümcül hata.
- **Overfitting backtest:** Yüzlerce parametre deneyip "altın strateji" bulmak →
  gürültü ezberi → canlıda çöküş (Modül 04 çoklu test, Modül 08).
- **Rejim değişimi:** Piyasa dinamikleri değişir; geçmişte çalışan gelecekte
  çalışmayabilir. Modeli sürekli yeniden değerlendir.

---

## 🎯 Alıştırma

1. BTC kapanış fiyatına ve getirisine ADF testi uygula. Hangisi durağan? Fiyatın
   ACF/PACF'sini çiz, getiriyle karşılaştır.
2. Getiriye ARIMA, oynaklığa GARCH(1,1) uydur. 5 gün ileri getiri ve oynaklık
   tahmini yap. Oynaklık tahmini gerçekle ne kadar uyumlu?
3. ML yaklaşımı: gecikmeli getiriler + hareketli ortalama + takvim özellikleriyle
   LightGBM kur (TimeSeriesSplit!). Naive "yarın=bugün yönü" baseline'ını
   yenebiliyor musun? (Çoğu zaman zor — bu finansal gerçektir.)

---

## ✅ Kontrol listesi

- [ ] Otokorelasyon yüzünden zaman serisinin neden özel olduğunu biliyorum.
- [ ] Durağanlık kavramını ve nasıl sağlanacağını (fark alma) biliyorum.
- [ ] ARIMA(p,d,q)'nun parçalarını anlıyorum.
- [ ] GARCH'ın oynaklık kümelenmesini neden modellediğini biliyorum.
- [ ] Zaman serisinde doğrulamanın (walk-forward) farkını ve look-ahead bias'ı biliyorum.

Sonraki → [Modül 13: Nedensellik & EconML](13-nedensellik-econml.md)
