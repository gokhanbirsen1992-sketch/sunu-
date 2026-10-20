# 01 — Uçuş: Antalya (AYT) ⇄ Hamburg (HAM), 7–13 Aralık 2026

**Sorgu damgası:** 2026-10-20 13:09 UTC (sorgu tarihi 2026-10-20) · 1 yetişkin · economy · fiyatlar gidiş-dönüş TOPLAM, kişi başı
**Araç durumu:** SlickTrip MCP ✅ · Turkish Airlines MCP ✅ (çıktılar dosyaya kaydedildi, jq ile tamamı okundu: 29 gidiş / 40 dönüş seçeneği) · **WebFetch çalışmadı** (tüm havayolu siteleri + tcmb.gov.tr: DNS `ENOTFOUND`, 2 deneme) · **curl → tcmb.gov.tr çalışmadı** (proxy 403). Bagaj kuralları bu yüzden resmî sayfadan değil WebSearch özetlerinden alındı → `[doğrulanmalı]`.

## Özet
- AYT→HAM **direkt uçuş var**: SunExpress XQ170 (her gün görünüyor, 10:40→12:45) ve Pegasus PC5041 (6 ve 8 Aralık'ta listelendi, 7 Aralık'ta yok). Dönüşte direkt: Corendon XC151 (19:10), Pegasus PC5042 (15:40), SunExpress XQ171 (13:35). `[kesin]`
- En ucuz gidiş-dönüş: **198 USD** (AJet SAW aktarmalı + Corendon direkt dönüş). En ucuz direkt/direkt: **213 USD** (SunExpress + Corendon, 2 ayrı bilet). Tek biletle direkt/direkt: Pegasus 227 USD (8 Ara kalkış) veya SunExpress 247 USD (7 Ara kalkış). `[kesin]`
- THY (IST aktarmalı, tek bilet, 8 kg kabin dâhil): **19.121,77 TRY** en düşük; 23 kg bagajlı 20.061,77 TRY. `[kesin]` ≈ 345–362 EUR `[çıkarım]` — düşük maliyetlilerin ~1,8 katı.
- **ÖNERİLEN:** Gidiş **XQ170 — 7 Ara 10:40 AYT → 12:45 HAM**; Dönüş **XC151 — 13 Ara 19:10 HAM → 14 Ara 01:10 AYT**. Toplam 213 USD (≈190 EUR). Alternatif dönüş: XQ171 13 Ara 13:35 HAM → 19:10 AYT (toplam 247 USD, tek SunExpress bileti).
- İstanbul kalkışlı alternatif kazandırmıyor: SAW→HAM direkt g/d 205 USD + AYT–IST bağlantısı → AYT direkt 213 USD'den ucuza gelmez. `[çıkarım]`

## Kur notu
TCMB 20 Ekim 2026 resmî kuru çekilemedi (**bulamadım**). Bilgi amaçlı, 14 Ekim 2026 haber sitesi anlık kuru `[doğrulanmalı]` [K9]: USD 49,38/49,40 TRY · EUR 55,36/55,43 TRY · EUR/USD 1,1210. Aşağıdaki EUR/TRY karşılıkları bu kurla hesaplandı → hepsi `[çıkarım]`.

## Tablo 1 — AYT ⇄ HAM gidiş-dönüş seçenekleri (SlickTrip, USD toplam)
Kaynak: SlickTrip `search_flights` / `search_return_flights` / `booking_options` [K1–K4]. Saatler yerel. Rezervasyon linkleri **1 gün** geçerli (SlickTrip notu).

| # | Havayolu | Uçuş no | Gidiş (kalkış→varış) | Dönüş (kalkış→varış) | Süre | Aktarma | Fiyat | ≈EUR | Bagaj dâhil mi | Link | Etiket |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A1 | AJet + Corendon | VF3029+VF77 / XC151 | 8 Ara 07:40 AYT → 14:35 HAM | 13 Ara 19:10 HAM → 14 Ara 01:10 AYT | 8h55 / 4h00 | SAW 4h00 / direkt | **198 USD** (AJet 98 + Corendon 101, 2 ayrı bilet) | ~177 | AJet: tarife bilinmiyor; Corendon: tarife bilinmiyor → §Bagaj | AJet: https://mcp.slicktrip.com/book/bk_437b7c1cf5a82e43 · Corendon: https://mcp.slicktrip.com/book/bk_14da15526bf1cd7a | [kesin] |
| A2 | AJet + Corendon | VF3041+VF77 / XC151 | **7 Ara** 03:55 AYT → 11:15 HAM | 13 Ara 19:10 → 01:10(+1) | 9h20 / 4h00 | SAW 4h25 / direkt | 198 USD | ~177 | aynı | search_url [K1] (itinerary it_e6c66058173e77b0) | [kesin] |
| B1 | SunExpress + Corendon | XQ170 / XC151 | **7 Ara 10:40 AYT → 12:45 HAM** | **13 Ara 19:10 HAM → 14 Ara 01:10 AYT** | 4h05 / 4h00 | direkt / direkt | **213 USD** (XQ 113 + XC 101, 2 ayrı bilet) | ~190 | SunExpress: tarife belirtilmedi; Corendon: tarife belirtilmedi | XQ: https://mcp.slicktrip.com/book/bk_15e6d9974e254fe7 · XC: https://mcp.slicktrip.com/book/bk_96a33fc9d19af0f9 | [kesin] |
| B2 | SunExpress + Pegasus | XQ170 / PC5042 | 7 Ara 10:40 → 12:45 | 13 Ara 15:40 HAM → 21:10 AYT | 4h05 / 3h30 | direkt / direkt | 232 USD | ~207 | – | search_url [K1] (it_f471d3caf205dadc) | [kesin] |
| B3 | SunExpress (tek bilet) | XQ170 / XQ171 | 7 Ara 10:40 → 12:45 | 13 Ara 13:35 HAM → 19:10 AYT | 4h05 / 3h35 | direkt / direkt | **247 USD** (SunExpress direkt satış) | ~220 | tarife belirtilmedi | https://mcp.slicktrip.com/book/bk_cdf15522816739b1 (wego 417, Gotogate 439 USD — pahalı) | [kesin] |
| C1 | Pegasus + Corendon | PC5041 / XC151 | 8 Ara 09:05 AYT → 10:50 HAM | 13 Ara 19:10 → 01:10(+1) | 3h45 / 4h00 | direkt / direkt | **203 USD** (PC 103 + XC 101, 2 ayrı bilet) | ~181 | Pegasus muhtemelen Light (sadece koltuk altı çanta) | PC: https://mcp.slicktrip.com/book/bk_0060f90f0425bdf8 · XC: https://mcp.slicktrip.com/book/bk_65f66a58da49cd5f | [kesin] |
| C2 | Pegasus (tek bilet) | PC5041 / PC5042 | 8 Ara 09:05 → 10:50 | 13 Ara 15:40 → 21:10 | 3h45 / 3h30 | direkt / direkt | **227 USD Light** · Saver 279 · Saver Plus 313 · Comfort Flex 331 | ~203 | Light: koltuk altı çanta yalnız; Saver+: 8 kg kabin + 20 kg bagaj [doğrulanmalı] | Light: https://mcp.slicktrip.com/book/bk_4153fe0c3976d311 · Saver: https://mcp.slicktrip.com/book/bk_c2e756af29d05ef3 · Saver Plus: https://mcp.slicktrip.com/book/bk_49963652ab1496c6 · Comfort Flex: https://mcp.slicktrip.com/book/bk_6a113317b6c19736 | [kesin] |
| D | Pegasus (SAW aktarmalı) | PC2023+PC1043 | 7 Ara 05:20 AYT → 10:35 HAM | (en ucuz dönüşle) | 7h15 | SAW 2h40 | 225 USD | ~201 | – | search_url [K1] | [kesin] |

Not: SlickTrip 222 fiyatlı seçenek buldu; tablo en ucuz 25 + direkt filtresi üzerinden seçildi. 7 Aralık'ta Pegasus direkt uçuş listelenmedi (6 Ara 13:10 ve 8 Ara 09:05 var). AJet'in SAW'daki uzun/gecelemeli bağlantıları (11–21 saat) tabloya alınmadı.

## Tablo 2 — Turkish Airlines (IST aktarmalı, tek bilet, TRY)
Kaynak: Turkish Airlines MCP `search_flights` + `search_inbound_flights` (searchId a7d33c8e…), 7 Ara gidiş / 13 Ara dönüş [K5]. Fiyat = gidiş-dönüş toplam, 1 ADT.

| Gidiş | Dönüş | Süre | Marka | Bagaj | Değişiklik/İade | Toplam | ≈EUR/USD | Link | Etiket |
|---|---|---|---|---|---|---|---|---|---|
| TK2413 AYT 12:50→IST 14:25 + TK1663 IST 16:00→**HAM 17:20** | TK1666 **HAM 14:10**→IST 19:30 + TK2432 IST 22:10→AYT 23:30 | 6h30 / 7h20 | CL | 1×8 kg kabin, **bagaj yok** | yok / iade yok | **19.121,77 TRY** | ~345 EUR / ~387 USD | https://www.turkishairlines.com/en-us/flights/booking/deeplinkprofile?D=1&dom=0&prc=19121.77&cur=TRY&lp=PROM&retd=131226&f1=TK1666,TK2432&so1=1&fb1=L&bc1=CL&f0=TK2413,TK1663&dep=AYT&dst=HAM&depd=071226&pas=A:1&so0=1&cc=ECONOMY,ECONOMY&fb0=Y&bc0=CL | [kesin] |
| aynı | aynı | aynı | LG | 1×8 kg kabin + **23 kg** | 3.462 TRY ücretle / iade yok | 20.061,77 TRY | ~362 EUR / ~406 USD | …&bc1=LG (aynı deeplink, bc1=LG) | [kesin] |
| aynı | aynı | aynı | GN / FL | 23 kg / 30 kg | esnek | 20.901,77 / 21.890,77 TRY | ~377 / ~395 EUR | deeplink listesinde | [kesin] |
| Alternatif gidiş: TK2433 AYT 07:30→IST 09:05 + TK1665 IST 11:45→**HAM 13:05** (7h35) | TK1668 HAM 06:35→IST 12:00 + TK2418 IST 13:45→AYT 15:05 veya TK1662 HAM 10:40→IST 16:00 + TK2428 19:25→AYT 20:45 | – | CL | 8 kg kabin | – | gidiş 6.655,07 TRY aynı; dönüş TK1668/TK1662 ile toplam 20.703,77 TRY | ~374 EUR | search çıktısı | [kesin] |

THY fiyat takvimi (g/d tahmini, 6 gece, TRY, `find_flight_price_calendar` [K6]): gidiş 6 Ara 21.000 · **7 Ara 19.100** · 8 Ara 18.900 (en düşük) · 9–10 Ara 20.500. Dönüş (7 Ara gidiş için): 12 Ara 20.700 · 13 Ara 19.100 · 14 Ara 18.900 · 10 Ara 14.000 (en düşük). `[kesin]` (takvim tahmini; gerçek arama sonucu 19.121,77 ile uyumlu)

## Tablo 3 — Esnek tarih farkı (direkt uçuşlar, g/d toplam USD, SlickTrip [K1][K7][K8])
Her hücre: o gidişin en ucuz direkt dönüşle eşlenmiş toplamı (dönüş uçuş no compact çıktıda belirtilmedi; 13 Ara için XC151).

| Gidiş ↓ / Dönüş → | 12 Ara (Cmt) | 13 Ara (Paz) | 14 Ara (Pzt) |
|---|---|---|---|
| **6 Ara (Paz)** | – (sorgulanmadı) | PC5041 13:10→14:55: 238 · XQ170: 247 | PC: 273 · XQ: 281 |
| **7 Ara (Pzt)** | XQ170: 247 | **XQ170: 213** (Pegasus direkt yok) | XQ170: 247 |
| **8 Ara (Sal)** | PC5041: 238 · XQ170: 247 | **PC5041: 203** · XQ170: 213 | PC5041: 238 · XQ170: 247 |

Aktarmalı dâhil en ucuz: 198 USD (AJet, 7 veya 8 Ara gidiş + XC151 13 Ara). SlickTrip'e göre bu rota için olağan aralık 132–230 USD; 7–8 Ara fiyatları "olağan" düzeyde, 8→14 Ara "olağandan yüksek". `[kesin]` Sonuç: **7→13 Ara (protokol tarihleri) fiyat açısından da iyi; 8→13 Ara 10 USD daha ucuz ama 1 gece eksik.** `[çıkarım]`

## Tablo 4 — İstanbul kalkışlı alternatif (IST_SAW → HAM, direkt, g/d USD) [K10]
| Havayolu | Uçuş | Gidiş | Toplam | Not |
|---|---|---|---|---|
| AJet | VF77 | 7 Ara SAW 09:50→HAM 11:15 | 205 | + AYT–SAW bağlantı maliyeti (AJet VF3041 vb., ayrıca alınmalı) |
| Pegasus | PC1043 | 7 Ara SAW 09:20→HAM 10:35 | 223 | + AYT–SAW |
| THY | TK1665 | 7 Ara IST 11:45→HAM 13:05 | 312 | + AYT–IST |
Karar: AYT direkt 213 USD varken İstanbul'dan başlamak anlamsız. `[çıkarım]`

## 3 Öneri
**(a) En ucuz — A2/A1: AJet + Corendon, 198 USD (~177 EUR).** 7 Ara 03:55 kalkış, SAW'da 4h25 bekleme, HAM 11:15; dönüş XC151 19:10. 15 USD tasarruf için 5 saat daha uzun yolculuk + gece 03:55 kalkış + 2 ayrı bilet; AJet Basic tarifede 8 kg kabin çantası bile dâhil olmayabilir [doğrulanmalı]. Tavsiye etmiyorum. `[çıkarım]`

**(b) En hızlı/direkt — B1: SunExpress XQ170 + Corendon XC151, 213 USD (~190 EUR) → ÖNERİLEN.** Protokol tarihleri (7→13 Ara, 6 gece), iki yönde direkt, öğlen varış (12:45) otel check-in'e uygun, dönüş 19:10 ile son gün tam kullanılır. İki ayrı bilet; ikisi de direkt olduğu için aktarma riski yok. `[çıkarım]`

**(c) En iyi denge — B3: SunExpress XQ170 + XQ171 tek bilet, 247 USD (~220 EUR).** Aynı havayolu, tek PNR, dönüş 13:35→19:10 (gece yarısı Antalya'ya varış yok). 34 USD fark karşılığı tek rezervasyon + ev'e akşam varış. Bagaj almayı planlayan için SunExpress'te 8 kg kabin/20 kg bagajlı tarife seçilmeli [doğrulanmalı]. `[çıkarım]`
Tek bilet + en ucuz direkt isteyen için C2 Pegasus 227 USD (8→13 Ara, 5 gece, Light = sadece koltuk altı çanta).

## Transfer/otel ajanları için kritik saatler (ÖNERİLEN B1)
- **Gidiş varış: 7 Aralık 2026 Pazartesi 12:45, HAM (yerel, CET)** — XQ170, direkt, 4h05. `[kesin]`
- **Dönüş kalkış: 13 Aralık 2026 Pazar 19:10, HAM (yerel)** — XC151, AYT varış 14 Aralık 01:10 (TRT). `[kesin]` (Alternatif: XQ171 13:35 kalkış, AYT 19:10 varış.)
- Antalya tarafı: XQ170 AYT kalkış 7 Ara 10:40 → evden (Muratpaşa) havalimanına en geç 08:30 civarı çıkılmalı (uluslararası, 2 saat önce). `[çıkarım]`

## Bagaj (WebFetch çalışmadığı için resmî sayfa doğrudan okunamadı; WebSearch özetleri — hepsi `[doğrulanmalı]`, THY hariç)
| Havayolu | Koltuk altı | Kabin (8 kg) | Bagaj | Kaynak |
|---|---|---|---|---|
| SunExpress | SunLight: 4 kg, 30×40×20 cm | SunLight'ta yok, +19,99 EUR'dan eklenir; SunValue/SunEco+/SunComfort'ta dâhil (55×40×23) | SunLight: yok; SunEco+: Antalya uçuşlarında 20 kg | [K11] (sunexpress.com sayfaları, arama özeti) |
| Pegasus | Light: 40×30×15 cm, 3 kg | Light'ta yok (ek ücretli); Saver/Saver Plus/Comfort Flex: 55×40×23, 8 kg | Light: yok; Saver ve üstü: 20 kg | [K12] flypgs.com genel kurallar/paketler (arama özeti) |
| Corendon (XC) | Promo/Lite: sadece 40×30×20 | Eco: 10 kg, 55×40×25 dâhil | Eco: yok; Comfort: 20 kg; Flex: 23 kg | [K13] corendonairlines.com/en/baggage (arama özeti) |
| AJet | Basic: 40×30×15, 4 kg | EcoJet/Flex/Premium: 8 kg 55×40×23; Basic'te yok (~12 EUR ek) | EcoJet: 20 kg (ikincil kaynak) | [K14] (ikincil; Aralık 2025 kural değişikliği) |
| THY | – | CL: **1×8 kg kabin dâhil** | CL: yok; LG/GN: 23 kg; FL: 30 kg | [K5] araç çıktısı `miniRulesInfoMap` → `[kesin]` |
SlickTrip'teki SunExpress 113 USD, Corendon 101 USD ve AJet 98 USD biletlerinin hangi tarife (Light/Eco/Basic) olduğu çıktıda belirtilmedi → ödeme sayfasında kontrol edilmeli.

## Kaynaklar
1. SlickTrip arama (AYT→HAM, 7–8 / 12–13 Ara, tüm uçuşlar): https://slicktrip.com/flights?key=AYT%3BHAM%3Beconomy%3B1%3B2026-12-07_2026-12-08%3B2026-12-12_2026-12-13&src=claude&utm_source=claude&utm_medium=mcp&utm_campaign=assistant&st_ref=2a7942c00f
2. SlickTrip 7→13 Ara (XQ170 dönüşleri): https://slicktrip.com/flights?key=AYT%3BHAM%3Beconomy%3B1%3B2026-12-07%3B2026-12-13&src=claude&utm_source=claude&utm_medium=mcp&utm_campaign=assistant&st_ref=2a7942c00f · takip linki: https://slicktrip.com/flights?key=AYT%3BHAM%3Beconomy%3B1%3B2026-12-07%3B2026-12-13&flights=XQ170&autosave=1&src=claude&utm_source=claude&utm_medium=mcp&utm_campaign=assistant&st_ref=2a7942c00f
3. SlickTrip 8→13 Ara (PC5041 / AJet dönüşleri): https://slicktrip.com/flights?key=AYT%3BHAM%3Beconomy%3B1%3B2026-12-08%3B2026-12-13&src=claude&utm_source=claude&utm_medium=mcp&utm_campaign=assistant&st_ref=2a7942c00f
4. SlickTrip `booking_options` (it_44a0c45c31979bae, it_ca422eb882a6160c, it_2a55c910e923a5ca, it_59fff7cf931e530f, it_74726bab2dc2bfff) — satıcı linkleri Tablo 1'de; 1 gün geçerli.
5. Turkish Airlines MCP `search_flights` (searchId a7d33c8e-d82f-4a93-bb0e-f2fcc982bf71) + `search_inbound_flights` (optionId 0 / rec 0, 13 Ara) — ham çıktı: `/root/.claude/projects/-home-user-sunu-/10800b23-0463-5d06-a7ba-13959a2368b1/tool-results/mcp-Turkish_Airlines-search_flights-1792501422186.txt` ve `…search_inbound_flights-1792501478931.txt`
6. Turkish Airlines MCP `find_flight_price_calendar` (AYT→HAM, ROUND_TRIP, 6 gece; gidiş anchor 2026-12-05, dönüş anchor 2026-12-07)
7. SlickTrip 6–7 Ara / 13–14 Ara direkt: https://slicktrip.com/flights?key=AYT%3BHAM%3Beconomy%3B1%3B2026-12-06_2026-12-07%3B2026-12-13_2026-12-14&stops=0&src=claude&utm_source=claude&utm_medium=mcp&utm_campaign=assistant&st_ref=2a7942c00f
8. SlickTrip 8→14 Ara direkt: https://slicktrip.com/flights?key=AYT%3BHAM%3Beconomy%3B1%3B2026-12-08%3B2026-12-14&stops=0&src=claude&utm_source=claude&utm_medium=mcp&utm_campaign=assistant&st_ref=2a7942c00f
9. Kur (14 Ekim 2026, haber sitesi, resmî değil): https://www.hisse.net/haber/dolar-ve-euro-bugun-kac-tl-14-ekim-2026-doviz-kurlari-102064 — TCMB today.xml erişilemedi.
10. SlickTrip IST_SAW→HAM direkt: https://slicktrip.com/flights?key=IST_SAW%3BHAM%3Beconomy%3B1%3B2026-12-07_2026-12-08%3B2026-12-12_2026-12-13&stops=0&src=claude&utm_source=claude&utm_medium=mcp&utm_campaign=assistant&st_ref=2a7942c00f
11. SunExpress bagaj: https://www.sunexpress.com/en/information/luggage-info/cabin-baggage · https://www.sunexpress.com/en-gb/book/book-your-trip/new-sunfares/ (WebSearch özeti)
12. Pegasus bagaj/paketler: https://www.flypgs.com/en/pegasus-baggage-allowance · https://www.flypgs.com/en/travel-services/flight-services/flight-packages · https://www.flypgs.com/en/generalrule/pdf (WebSearch özeti)
13. Corendon bagaj: https://www.corendonairlines.com/en/baggage (WebSearch özeti)
14. AJet bagaj (ikincil): https://travel-dealz.com/?p=107219 · https://baggagepolicies.com/anadolujet-baggage-policy/ (WebSearch özeti)
15. SlickTrip `route_airlines` AYT→HAM: direkt XQ (SunExpress), PC (Pegasus); aktarmalı EW, LH, TK, VF, LX, OS, EN, SN, WK.

## Açık noktalar / kullanıcı kararı gereken
1. **Dönüş saati seçimi:** XC151 19:10 (ucuz, son gün tam, AYT'ye 01:10 gece varış, ayrı bilet) mi, XQ171 13:35 (+34 USD, tek bilet, akşam 19:10 eve) mi? Otel/transfer ajanları B1 (19:10) ile planlıyor.
2. **Bagaj ihtiyacı:** 6 gece kış seyahati için 8 kg kabin yeterli mi, yoksa 20 kg bagaj mı? Cevaba göre tarife (SunValue/Saver/Eco/EcoJet) ve toplam fiyat değişir; ücretler sayfadan okunamadı.
3. SlickTrip satıcı linkleri 1 gün geçerli; fiyatlar anlık (20 Ekim 2026). Fiyat takibi için SlickTrip `track_flight` kurulabilir (kullanıcı onayı gerekli).
4. Pegasus 7 Aralık'ta AYT→HAM direkt uçmuyor gibi görünüyor (yalnızca 6 ve 8 Ara listelendi) — program değişirse 7 Ara 09:05 seçeneği doğabilir.
5. TCMB resmî kuru alınamadı; EUR karşılıkları yaklaşık.
