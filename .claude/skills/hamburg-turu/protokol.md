# Hamburg Turu — Ortak Ajan Protokolü

Bu dosya tüm `hamburg-*` ajanları için bağlayıcıdır. Her ajan işe başlamadan önce bunu okur.

## Varsayılan girdiler (orkestratör değiştirmediyse)
| Alan | Değer |
|---|---|
| Yolcu | 1 yetişkin |
| Kalkış şehri | Antalya (AYT) — ev: Güvenlik Mh. 262. Sk, Muratpaşa, Antalya |
| Gidiş | 7 Aralık 2026, Pazartesi |
| Dönüş | 13 Aralık 2026, Pazar |
| Süre | 6 gece (ISO 50. hafta = "Aralık 2. hafta") |
| Esneklik | Fiyat karşılaştırması için ±1 gün (6/8 Aralık gidiş, 12/14 Aralık dönüş) |
| Para birimi | EUR ana; TRY/USD bilgi amaçlı, kur kaynağı + tarihi yazılır |
| Sorgu tarihi | Çalıştırıldığı gün (`date +%F`), her fiyat tablosunun başına damga |

## Doğruluk kuralları (öncelik: doğruluk > hız > kapsam)
1. Load-bearing her olgusal iddia (fiyat, saat, süre, tarih, adres, kural, açılış saati) için **kaynak URL** ver VEYA açıkça **"bulamadım"** yaz. Boşluğu bellekten doldurma.
2. Sayılar araç çıktısından (SlickTrip / Turkish Airlines MCP) ya da açılan sayfadan birebir alınır. Araç çıktısındaki `search_url` / rezervasyon linki tabloya yazılır.
3. Güven etiketi yalnızca load-bearing iddialarda:
   - `[kesin]` — araç çıktısı veya resmî sayfadan birebir, bugün görüldü
   - `[doğrulanmalı]` — ikincil kaynak, eski tarihli sayfa veya 2026 için henüz ilan edilmemiş (ör. 2025 verisi)
   - `[çıkarım]` — hesap, toplam, yorum, öneri
4. Fiyatlar anlıktır; "sorgu tarihi" damgası olmadan fiyat yazma.
5. Hiçbir aracın çalışmadığı durumda bunu raporun başında belirt; tahmin üretme.
6. Çelişki görürsen (ör. uçuş iniş saati otel check-in'den sonra) açıkça yaz.

## Çıktı biçimi
- Türkçe, yoğun, dolgusuz; giriş cümlesi ve övgü yok.
- Sıra: kısa özet (≤5 satır) → tablolar → gün/gün ya da madde listesi → **Kaynaklar** (numaralı URL) → **Açık noktalar / kullanıcı kararı gereken**.
- Dosyaya yaz: `seyahat/hamburg-aralik-2026/<NN-ad>.md` (NN ajan numarası). Dosyayı yazdıktan sonra orkestratöre 10 satırı geçmeyen özet döndür; tam içerik dosyadadır.
