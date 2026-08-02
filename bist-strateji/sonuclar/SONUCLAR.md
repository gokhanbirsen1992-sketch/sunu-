# Turnuva ve Doğrulama Sonuçları

## 🥇 Momentum Rotasyonu (hisseler arası — endeksi geçmenin en sağlam yolu)

Tek sembol zamanlaması yerine kesitsel momentum (Jegadeesh-Titman 1993):
her ay, 6 aylık getirisi (son 1 ay atlanarak) en yüksek 5 hisseyi eşit
ağırlıkla tut; momentumu negatif olanlar alınmaz (Antonacci mutlak filtre).

Parametre taraması (8 bağımsız 20-hisselik sentetik evren, komisyon %0.1/bacak,
düşmanca inceleme sonrası adil kıyas penceresiyle — iki taraf da stratejinin
başladığı günden ölçülür):

| Pencere | Top-K | Rotasyon | Medyan CAGR farkı | Kazanma |
|---|---|---|---|---|
| **126g (6 ay)** | **5** | **Aylık** | **+6.52 puan/yıl** | **5/8** |
| 126g | 7 | Aylık | +5.13 | 5/8 |
| 126g | 3 | Aylık | +4.37 | 5/8 |
| 252g (12 ay) | 5 | Aylık | +0.22 | 4/8 |

Kazanan evrenlerde avantaj +10/+15 puan; kaybeden 3 evrende -1/-13 puan —
rotasyon bir garanti değil, olasılık avantajıdır.

Bulgular literatürle birebir: 6 ay > 12 ay; aylık > haftalık (komisyon);
konsantrasyon (top-3) varyansı artırıyor. Maks. düşüş HODL'dan ~4 puan yüksek
(5 hisse < 20 hisse çeşitlendirmesi) — rotasyonun bedeli. Kıyas: eşit ağırlık
evren al-tut. Uygulama: `BIST_Momentum_Rotasyon.pine` (gerçek BIST verisiyle
canlı simülasyon + sıralama tablosu + rotasyon alarmı).

İki turnuva, toplam **10 strateji ailesi**, ~1000 parametre kombinasyonu,
her kombinasyon 20-40 senaryoda (günlük + haftalık, %0.1 komisyon/bacak) test edildi.
Protokol: eğitim (seed 0-19) → ince ayar → out-of-sample (seed 100-114) →
**hiçbir optimizasyonda kullanılmamış** nihai onay seti (seed 200-214).

## 🏆 Kazanan: Rejim Filtresi

```
sma_gun = 131   (trend SMA, işlem günü; plato 131-150)
mom_gun = 284   (momentum penceresi, işlem günü; doğrulanmış bölge 284-315)
band    = %3    (histerezis çıkış bandı)
```

**Kural:** Varsayılan pozisyon LONG. Çıkış yalnızca çifte ayı teyidinde:
`kapanış < SMA×0.97 VE 284g momentum < 0`. Geri giriş: `kapanış > SMA VEYA momentum > 0`.

| Aşama | Skor | CAGR farkı (yıllık puan) | HODL'u geçme | MaksDD farkı | İşlem/10y |
|---|---|---|---|---|---|
| Eğitim (0-19) | +0.93 | -0.03 | %50 | -3.8 pp | 6 |
| **OOS (100-114)** | **+6.06** | **+1.54** | **%66.7** | **-18.1 pp** | 6 |
| **Nihai onay (200-214)** | **+1.65** | **+0.18** | **%60** | **-5.9 pp** | 8 |

Zaman dilimi: günlük hafif önde (onay setinde geçme %66.7 vs %53.3); ikisi de geçerli.

### Sınırlamalar (dürüst rapor)

- **Endeks profili için doğrulandı** (XU100 benzeri). Tekil hisse profilinde
  (1.5× volatilite) onay kriterlerini geçemedi (skor -0.04, geçme %36.7) —
  hissede yalnızca drawdown azaltma sağlıyor, getiri avantajı yok.
- Alpha asimetrik: ayı/yatay senaryolarda büyük kazanç (+3.8 medyan CAGR farkı,
  10/10 geçiş), güçlü boğada ≈ başabaş. Skorun ana kaynağı düşüş koruması.
- En kötü senaryo tipi: güçlü boğa içindeki V-tipi düzeltmede dipte satıp
  toparlanmada %3-10 pahalıya geri alma (seed 113 örneği).

## 🥈 İkinci doğrulanmış mod: Zirve İz Stop (tepeye yakın satış)

Kullanıcı geri bildirimi üzerine eklendi: rejim filtresinin çıkışları çifte
teyit beklediği için dibe yakın düşüyordu. Zirve İz Stop satışı **pozisyon
zirvesinden sabit mesafede** yapar — satış hiçbir zaman zirvenin %10'undan
fazla altında olmaz.

```
esik    = %10   (zirveden düşüş eşiği)
sma_gun = 100   (geri giriş SMA'sı)
mom_gun = 284   (geri giriş momentumu)
be      = 1     (breakeven geri giriş — açık)
```

**Kural:** Varsayılan LONG. SAT: kapanış < zirve×0.90. AL: kapanış > SMA(100g)
VEYA momentum > 0 VEYA kapanış çıkış fiyatını aşarsa (breakeven).

| Aşama | Skor | CAGR farkı | HODL'u geçme | MaksDD farkı | İşlem/10y |
|---|---|---|---|---|---|
| Eğitim (0-19) | +1.46 | +0.95 | %62.5 | -2.0 pp | 15 |
| OOS (100-114) | +1.95 | +0.25 | %53.3 | -6.8 pp | 19 |
| Nihai onay (200-214) | +0.78 | +0.09 | %53.3 | -2.8 pp | 18 |

Rejim filtresine göre: daha fazla işlem (komisyon yükü), benzer toplam skor,
ama satışlar tepeye yakın — psikolojik olarak çok daha rahat izlenir.
Aynı sınırlama geçerli: **endeks profili** (hisse profilinde onayda kaldı).
İlginç not: breakeven geri giriş, rejim filtresinde zararlıyken bu ailede
faydalı — hızlı çıkışların yanlış alarm oranı yüksek olduğu için sigorta işliyor.

## ❌ Test edilip reddedilen: "Tepede sat, dipte al" bandı (mean reversion)

Kullanıcının istediği "güce satış" mantığı (sapma > eşik iken sat, ortalamaya
dönünce al) 216 kombinasyonla tarandı: **gerçekten tetiklenen her tepe-satış
eşiği para kaybetti** (eşik %20 → skor -16, HODL'u geçme %0). Optimizasyon,
eşiği ulaşılmaz %55'e itip özelliği fiilen kapattı — yani veri, trendli
piyasada mekanik tepe satışının anti-alpha olduğunu söylüyor. Literatürle
tutarlı: momentum piyasasında kazananı erken satmak en pahalı hatadır
(Jegadeesh-Titman 1993; "cut winners short" sendromu).

## Elenen yaklaşımlar ve nedenleri

| Aile | Eğitim | OOS | Neden |
|---|---|---|---|
| Komposit 6'lı oylama | +5.07 | **-2.89 → KALDI** | Ağır overfit; sık çıkış + pahalı geri giriş |
| Supertrend (+ADX) | +5.79 | **-2.81 → KALDI** | Aynı mekanizma; ADX filtresi hiç değer katmadı |
| EMA kesişimi + MACD | -5.1 | — | Eğitimde bile HODL'a sistematik yenik |
| Donchian/Turtle | +2.69 | — | Boğa geri çekilmelerinde pozisyon boşaltıyor |
| KAMA + ROC | -0.44 | — | 110+ işlemin komisyon yükü |
| RSI ortalamaya dönüş | -21.8 | — | Trendli piyasada nakit bekleyip ralli kaçırıyor; çöküşte "düşen bıçak" |
| Faber SMA (100g, %5 bant) | +0.28 | +4.47 | Nihai onayda geçme %36.7 < %40 → **KALDI** (hissede savunma amaçlı kabul edilebilir) |
| Mutlak momentum | -0.70 | — | Tek başına yetersiz; rejim filtresinin bileşeni olarak değerli |
| Yavaş Supertrend | +0.07 | — | Geniş çarpan hem korumayı hem getiriyi kaybediyor |
| Breakeven geri giriş kuralı | — | — | Test edildi, medyanda **zararlı** çıktı (-0.12), kapatıldı |

## Yorum

Bu sonuçlar literatürle tutarlı: güçlü nominal sürüklenmeli bir piyasada (TL
bazlı BIST) long/flat zamanlama sistemlerinin ana değeri **büyük ayıları
atlamaktır**; getiri farkı ise ancak yavaş, az işlemli, çifte teyitli
filtrelerle pozitife geçer (Faber 2007; Antonacci 2014; Zakamulin 2017;
Moskowitz-Ooi-Pedersen 2012). Hızlı sinyal aileleri (MACD kesişimleri, kısa
EMA'lar, oylama sistemleri) eğitim verisinde parlak görünüp örneklem dışında
çöker — klasik aşırı uyum. Bu depodaki 3 aşamalı protokol tam da bunu ayıkladı.

Ham turnuva çıktıları: `turnuva1_hizli_aileler.json`, `turnuva2_yavas_rejim.json`.
