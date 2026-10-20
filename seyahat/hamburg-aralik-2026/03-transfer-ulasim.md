# 03 — Transfer ve Ulaşım (Hamburg, 7–13 Aralık 2026)

**Sorgu damgası: 2026-10-20** · Yolcu: 1 yetişkin · Para birimi: EUR (Antalya bacağı TRY)
**Araç durumu:** WebFetch ve curl ile resmî sayfalara doğrudan erişim proxy tarafından engellendi (DNS/403). Tüm veriler WebSearch'ün resmî sayfalardan döndürdüğü alıntılardan alındı; `[kesin]` = resmî alan adından (hvv.de, hamburg.de, hamburg-airport.de, bahn.de, nah.sh, hadag.de, antalya-airport.aero, havayolu siteleri) bugün görülen alıntı. Arama bütçesi son sorguda doldu (bkz. Açık noktalar #1). TRY↔EUR kuru çekilemedi; TRY tutarları çevrilmedi.
**Uçuş saatleri belli değil:** "varsayım" etiketli her satır uçuş saati netleşince yeniden hesaplanmalı.

## Özet
- HAM → Hauptbahnhof: S1, 25 dk, 10 dk'da bir; hvv Einzelkarte Hamburg AB 4,10 € (app 3,81 €), havalimanı AB bölgesinde. S1 ~04:00–01:00, hafta sonu gece boyunca. Gece varışta taksi ~33–37 € (hesap) / ön rezervasyonlu sabit 38 € (≤12 km).
- Antalya ev → AYT: taksi önerilir (~20 dk; UKOME 2026 tarifesiyle ~700–850 TL hesap, `[doğrulanmalı]`); AntRay T1 havalimanına gider ama Güvenlik Mh.'ye en yakın durak ve sefer sıklığı resmî kaynakta bulunamadı.
- 6 gün bilet kararı: Lübeck günübirliği yapılacaksa **Deutschlandticket 63 €** (hvv + RE Lübeck dâhil) en ucuz; yapılmayacaksa hvv Gesamtnetz Wochenkarte 43 € (geçerlilik kuralı doğrulanmalı) ya da günlük app bileti 7×7,63 = 53,41 €. Hamburg CARD (5 gün 54,90 €) yalnızca ≥3 ücretli müze/tur planlanıyorsa mantıklı.
- Lübeck: RE8/RE80 43–46 dk, günde ~40 sefer; SH-Tarif tek yön 18,90 €, Schleswig-Holstein-Ticket 34 € (hafta içi 09:00'dan itibaren), Deutschlandticket geçerli.
- Bulunamayanlar: S1 ilk/son tren dakikası, gece otobüsü 606'nın havalimanına gidip gitmediği, HAM resmî taksi ücret tahmini, Havaş Antalya ücreti/saati, AntRay resmî sefer aralığı, Antalya Ekim 2026 zam kararının sonucu, Güvenlik Mh.→AYT km.

## 1. Antalya ev (Güvenlik Mh. 262. Sk, Muratpaşa) → AYT

| Bacak | Seçenek | Süre | Fiyat | Sıklık/Saat | Kaynak | Etiket |
|---|---|---|---|---|---|---|
| Ev → AYT | Taksi (taksimetre) | ~20 dk merkez→AYT (D400) | Açılış 40 TL + 50 TL/km, indi-bindi min. 200 TL, bekleme 240 TL/sa (UKOME, 23 Mart 2026'dan itibaren) → 13–16 km `[varsayım]` için **690–840 TL** | 24 saat | [16] süre; [23][24] tarife | süre `[kesin]`, tarife `[doğrulanmalı]` (üçüncü taraf haber, UKOME kararı doğrudan görülmedi), tutar `[çıkarım]` |
| Ev → AYT | AntRay T1 tramvay (Havalimanı Gidiş durağı, viyadük) | bulamadım (Meydan→Havalimanı süresi resmî kaynakta yok) | Antalyakart tam 42 TL; kullan-at 46 TL; temassız banka kartı 50 TL (Mart 2026 tarifesi) | Havalimanı kolu ~20 dk'da bir, ~05:50–23:23 `[doğrulanmalı]` (üçüncü taraf, tarihli); resmî saatler: antalyaulasim.com.tr "Hareket Saatleri", Antalyakart Mobil, 0242 606 07 07 | [25][26][27][28] | ücret `[doğrulanmalı]` (12 Ekim 2026 meclisinde 53 TL'ye zam gündemdeydi, sonuç bulunamadı); durak/saat `[doğrulanmalı]` |
| Ev → AYT | Havaş | bulamadım | bulamadım (resmî havas.net verisi arama sonuçlarına girmedi) | bulamadım | — | — |
| Ev → AYT | Belediye otobüsü 600 (Otogar–Havalimanı) | ~60 dk `[doğrulanmalı]` | 70 TL `[doğrulanmalı]` | Havalimanından ilk 06:35 / son 01:05 `[doğrulanmalı]` | [29] | Güvenlik Mh.'den Otogar'a gitmek gerekir; pratik değil |

- Güvenlik Mh.'ye en yakın AntRay durağı: **bulamadım** (Meydan veya Sinan olması muhtemel, `[varsayım]`; kullanıcı haritadan teyit etmeli).
- **Gündüz kalkış senaryosu** `[varsayım]`: Taksi; evden çıkış = kalkış − (uluslararası için havayolu önerisi 3 sa [31]) − 25 dk yol − 15 dk tampon ≈ **kalkıştan 3 sa 40 dk önce**. Minimum: kontuar kapanışı kalkıştan 60 dk önce (THY/Pegasus/SunExpress) [31][32][33].
- **Gece / erken sabah kalkış senaryosu (örn. 05:00–07:30)** `[varsayım]`: Tramvay ilk seferi havalimanına ~06:00 civarı ulaşır → yetmez; **taksi tek seçenek**. Gece tarifesi farkı: UKOME 2026 haberlerinde gece zammı geçmiyor `[doğrulanmalı]`.

## 2. HAM → şehir (otel Hauptbahnhof çevresi varsayıldı `[varsayım]`)

| Bacak | Seçenek | Süre | Fiyat | Sıklık/Saat | Kaynak | Etiket |
|---|---|---|---|---|---|---|
| HAM → Hbf | S-Bahn S1 (istasyon terminallerin önünde; Ohlsdorf'ta tren bölünür, yalnızca **ön 3 vagon** Airport'a gider — dönüşte de ön 3 vagona binilmeli) | **25 dk** | Einzelkarte Hamburg AB **4,10 €** (hvv switch app **3,81 €**, %7 online indirim); havalimanı Hamburg AB'de | **10 dk'da bir**; işletme ~04:00–01:00, hafta sonu/tatil gece boyunca; ilk/son tren dakikası bulamadım | [1][2][3][4][5] | `[kesin]` |
| HAM → Hbf | Taksi (durak T1/T2 varış katı önü; kart ödemesi) | ~20–25 dk `[varsayım]` | Hamburg resmî tarifesi: açılış 4,50 € + 2,70 €/km (ilk 9 km) + 2,00 €/km (sonrası); 11–13 km `[varsayım]` için **~33–37 €**. Ön rezervasyonlu sabit fiyat: 38 € (≤12 km) / 52 € (12–20 km). Havalimanı sayfasında ücret tahmini yok. | 24 saat | [6][7][8] | tarife `[doğrulanmalı]` (Şubat 2025 belgesi, 2026 değişikliği bulunamadı); tutar `[çıkarım]` |
| HAM → Hbf | Otobüs 292 (terminal önü) + aktarma | — | hvv tarifesi | 10 dk'da bir | [2] | `[kesin]` |
| HAM → şehir | Gece otobüsü 606 | bulamadım (havalimanına uğrayıp uğramadığı teyit edilemedi) | — | — | [2] | `[doğrulanmalı]` |

- **Gündüz varış senaryosu** (iniş 05:00–00:30 arası) `[varsayım]`: bagaj + pasaport sonrası S1; app'ten Einzelkarte 3,81 € (aynı gün ≥3 biniş olacaksa Tageskarte 7,63 €; Deutschlandticket alındıysa ek bilet yok). Kapı-kapı ~45–55 dk `[çıkarım]`.
- **Gece varış senaryosu** (Pazartesi gecesi ~00:30–04:00 iniş) `[varsayım]`: 7 Aralık Pazartesi hafta içi → S1 gece çalışmaz; **taksi** (~33–37 € hesap; sabit fiyat için önceden Hansa-Taxi/Taxiruf/FreeNow ile rezervasyon [6]). Yedek: ilk S1 ~04:00.
- Türk vatandaşları için HAM pasaport kontrolü/bekleme süresi: bulamadım; yazılmadı.

## 3. Hamburg içi ulaşım — tarife ve seçenekler (2026)

| Ürün | Kapsam | Fiyat | Kural | Kaynak | Etiket |
|---|---|---|---|---|---|
| hvv Einzelkarte Hamburg AB | Ring A+B (havalimanı dâhil), tek yön | 4,10 € / app 3,81 € | — | [1][3][5] | `[kesin]` |
| hvv Kurzstrecke | kısa mesafe | 2,10 € | — | [5] | `[kesin]` |
| hvv Tageskarte Hamburg AB | gün boyu, ertesi 06:00'ya kadar | 8,20 € / app 7,63 € | 9-Uhr-Tageskarte **kaldırıldı** (hvv 2024 tarife notu) | [3][5][9] | `[kesin]` |
| hvv Gesamtnetz Wochenkarte | tüm hvv ağı, 7 gün | 43,00 € (2027'de kalkıyor) | 7 günün başlangıç kuralı/aktarılabilirlik bulamadım; Hamburg AB'ye özel Wochenkarte bulamadım | [5][10] | fiyat `[kesin]`, kural `[doğrulanmalı]` |
| hvv Any (hvv switch app) | check-in/out ile gün sonunda en ucuz bilet hesaplanır | kullanım kadar | günlük tavan tutarı bulamadım | [11] | `[kesin]` |
| Hamburg CARD (Einzel: 1 yetişkin + 3 çocuk) | hvv Hamburg AB (havalimanı dâhil) + 150+ sunumda %50'ye varan indirim; 1–5 ardışık gün; son gün ertesi 06:00'ya kadar | 1 gün 12,90 · 2 gün 24,90 · 3 gün 35,90 · 4 gün 46,90 · 5 gün 54,90 €; grup (5 kişi) 1 gün 24,90 / 5 gün 94,90 € | 6 günlük yok; satış: online, otomat, hvv app, havalimanı turist danışma | [12][13][14] | `[doğrulanmalı]` — hamburg-tourism.de'de 11,90/22,90/33,50/44,50/51,50 € eski görünümlü ikinci bir fiyat seti dolaşımda; hvv.de ana sayfası 12,90 €'dan başlıyor |
| Deutschlandticket | Almanya geneli RE/RB + tüm hvv (Lübeck dâhil); ICE/IC hariç | **63 €/ay** (1 Oca 2027'den 66,80 €) | Yalnız abonelik; ay ortası alımda **tam takvim ayı** ücreti; iptal ayın **10'una kadar**; 10'undan sonra alınırsa sonraki ay da ödenir; ödeme: kredi kartı (3D Secure), PayPal, SEPA (bahn.de/DB Navigator) | [15][17][18] | kurallar `[kesin]`; yurt dışı kartla sorunsuz abonelik `[doğrulanmalı]` |
| StadtRAD (bisiklet) | hvv switch'ten de kiralanıyor (Haz 2026) | Temel ücretli tarifede ilk 30 dk ücretsiz; Light (temel ücretsiz) 0,14 €/dk (EN sayfada 0,10), günlük tavan 12 €; yıllık 8,90 € (10 € kredi dâhil) sonra 0,10 €/dk; D-Ticket tarifesi 0,08 €/dk | Hamburg CARD ile %20 (eski sayfa) | [19][20] | `[doğrulanmalı]` (resmî sayfalar çelişiyor) |
| HADAG feribot 62 (Landungsbrücken Brücke 3 → Fischmarkt → Dockland → Övelgönne → Bubendey-Ufer → Finkenwerder) | hvv bileti geçerli (ek ücret yok) | hvv tarifesi | Hafta içi 06:45–22:15 ~15 dk'da bir, dışında 30 dk; Cmt 05:45'ten; Paz 06:45'ten; gelgite bağlı; yaz tarifesi 30.03–01.11.2026, **Aralık kış tarifesi doğrulanmalı** | [21][22] | bilet `[kesin]`, Aralık sıklığı `[doğrulanmalı]` |

## 4. Günübirlik Lübeck

| Bacak | Seçenek | Süre | Fiyat | Sıklık/Saat | Kaynak | Etiket |
|---|---|---|---|---|---|---|
| Hamburg Hbf ⇄ Lübeck Hbf | RE8 / RE80 (DB Regio SH) | en hızlı 43 dk, tipik 43–46 dk | SH-Tarif Einzelkarte **18,90 €** tek yön (1 Nis 2026'dan) → gidiş-dönüş 37,80 €; SH-Tarif Tageskarte 35,40 € | günde ~40 bağlantı; akşam 20–24 ve hafta sonu ~30 dk'da bir | [34][35][36] | `[kesin]` |
| aynı | Schleswig-Holstein-Ticket (1 kişi) | aynı | **34 €** (otomat/dijital; gişede +2 €); 2 kişi 40, 3 kişi 46, 4 kişi 52, 5 kişi 58 € | Hafta içi **09:00**–ertesi 03:00; Cmt/Paz ve 24/31 Aralık 00:00'dan itibaren; SH + HH + MV RE/RB 2. sınıf | [37][38] | `[kesin]` |
| aynı | Deutschlandticket | aynı | 63 €/ay içinde | tüm RE/RB | [15][36] | `[kesin]` |

- Lübeck hvv bölgesinde değil → Hamburg AB biletleri/Hamburg CARD Lübeck'e geçmez `[çıkarım]`.
- 19 Ekim–12 Aralık 2026 Lübeck Hbf–Büchen kapalı (Lüneburg yönü); Hamburg–Lübeck hattını etkilemediği belirtiliyor `[doğrulanmalı]` [34].
- 13 Aralık 2026 DB tarife değişikliği günü = dönüş günü; Lübeck ve S1 saatleri 13 Aralık'ta değişebilir → bahn.de'den kontrol `[çıkarım]`.

## 5. Dönüş: otel → HAM (13 Aralık 2026, Pazar)

| Konu | Bilgi | Kaynak | Etiket |
|---|---|---|---|
| Hbf → HAM S1 | 25 dk, 10 dk'da bir; Cmt→Paz gecesi S1 gece boyunca çalışır (hafta sonu kuralı) | [1][4] | `[kesin]` |
| Havalimanı önerisi | Kalkıştan ~2 sa önce (tatil dönemi: en az 2 sa); kontuarlar genelde 2–3 sa önce açılır | [39][40] | `[kesin]` |
| Self Bag Drop | T1 ve T2'de; biniş kartıyla kalkış günü istenen saatte; süre 15–20 sn; vergi iadesi/boyutlu bagaj hariç; havayoluna bağlı. Üçüncü taraf: 04:00–20:30 | [41] | `[kesin]`; saat aralığı `[doğrulanmalı]` |
| Bir önceki akşam check-in | Bazı havayolları 18:00–20:00 arasında ertesi gün uçuşları için bagaj alır (son uçuş saati sınırı EN sayfada 10:00, DE'de 12:00 — çelişkili) | [41] | `[doğrulanmalı]` |
| Slot&Fly | Güvenlik kontrolü için ücretsiz 15 dk randevu; 72 sa öncesinden en geç 1 sa öncesine kadar | [42] | `[kesin]` |
| Havayolu kuralı (hangisi olacağı bilinmiyor) | THY: uluslararası check-in/bagaj kalkıştan **60 dk** önce kapanır, 3 sa önce gelme önerisi; Pegasus: 60 dk; SunExpress: 60 dk (HAM online check-in 72 sa–1 sa) | [31][32][33] | `[kesin]` |
| Önerilen zamanlama `[çıkarım]` | Otelden çıkış = kalkış − 2 sa (havalimanı) − 25 dk S1 − 10 dk yürüme/bekleme − 15 dk tampon ≈ **kalkıştan 2 sa 50 dk önce**; THY 3 sa önerisine uyulacaksa 3 sa 50 dk | — | `[çıkarım]` |

## 6. AYT → ev (gece varış senaryosu)

| Seçenek | Süre | Fiyat | Saat | Kaynak | Etiket |
|---|---|---|---|---|---|
| Taksi (T1 varış çıkışında durak, ücret panosu durağın yanında, sürücü havalimanı kimlikli) | ~20 dk | ~690–840 TL `[çıkarım]` (UKOME tarifesiyle) | **24 saat** (T1 için resmî SSS "evet") | [16][30] | durak/24 sa `[kesin]`, tutar `[doğrulanmalı]` |
| AntRay T1 (Havalimanı Geliş durağı, varış terminali karşısı) | bulamadım | 42–50 TL | son sefer ~23:23 `[doğrulanmalı]` | [26][27] | `[doğrulanmalı]` |
| Otobüs 600 → Otogar | ~60 dk | 70 TL `[doğrulanmalı]` | son 01:05 `[doğrulanmalı]`; eve gitmez | [29] | `[doğrulanmalı]` |

## Önerilen zincir (tek satır / bacak) + yedek
1. **Ev → AYT:** Taksi (~20 dk, ~700–850 TL `[çıkarım]`). Yedek: AntRay T1 (gündüz, en yakın durak teyit edilince).
2. **HAM → otel:** S1, 25 dk, app bileti 3,81 € (D-Ticket varsa 0 €). Yedek: taksi ~33–37 € / sabit 38 € (gece 01:00–04:00 arası tek seçenek).
3. **Hamburg içi:** Deutschlandticket (Lübeck planı varsa) / Wochenkarte 43 € veya günlük app bileti (yoksa); feribot 62 bilete dâhil.
4. **Lübeck:** RE8/RE80 ~45 dk; D-Ticket ile 0 €, yoksa SH-Ticket 34 € (hafta içi 09:00 sonrası; Cmt 12 Aralık ise 00:00'dan).
5. **Otel → HAM:** S1; kalkıştan ~2 sa 50 dk önce otelden çık. Yedek: taksi sabit fiyat 38 €.
6. **AYT → ev:** Taksi 24 sa, ~20 dk. Yedek: AntRay (23:23 öncesi iniş).

## Bilet kararı — 7 takvim günü (7–13 Aralık; "6 gece") `[çıkarım]`
Varsayım: her gün ≥3 hvv binişi; havalimanı transferleri dâhil (Hamburg AB). 6 gün hesabı parantezde.

| Seçenek | Hesap | Toplam (Lübeck hariç) | + Lübeck gidiş-dönüş | Toplam |
|---|---|---|---|---|
| A. Günlük app bileti | 7 × 7,63 € (6 × 7,63 = 45,78) | 53,41 € | SH-Ticket 34 € | **87,41 €** |
| B. Gesamtnetz Wochenkarte | 43,00 € (7 gün; başlangıç kuralı doğrulanmalı) | 43,00 € | SH-Ticket 34 € | 77,00 € |
| C. Deutschlandticket | 63 € (Aralık ayı tamamı) | 63,00 € | 0 € | **63,00 €** |
| D. Hamburg CARD 5 gün + 2 günlük app | 54,90 + 2 × 7,63 | 70,16 € | SH-Ticket 34 € | 104,16 € |
| E. Sadece Einzelkarte | 3,81 €/biniş; 2 biniş = 7,62 € ≈ Tageskarte 7,63 € → ≥3 binişte günlük bilet kazanır | — | — | — |

- **Karar:** Lübeck yapılacaksa **C (Deutschlandticket, 63 €)**: 1–7 Aralık arasında DB Navigator/bahn.de'den al (hvv switch de satar), **en geç 10 Aralık'ta iptal et** (aksi hâlde Ocak 2027 için 66,80 € daha çekilir). Lübeck yoksa **B (43 €)** — Wochenkarte'nin 7 Aralık'tan başlatılabildiği teyit edilemezse **A (53,41 €)**.
- Hamburg CARD, A'ya göre günde ~3,35 € prim ödetir (5 gün ≈ 16,75 €); müze/tur indirimleri bu tutarı aşacaksa (≈3 ücretli giriş) tercih edilebilir; Lübeck'i kapsamaz.
- Taksi gece varışı (yaklaşık 35 €) hiçbir bilete dâhil değildir; uçuş saati kesinleşince bu kalem eklenir/çıkar.

## Kaynaklar
1. https://www.hamburg-airport.de/en/arrival-and-departure-to-the-airport-36990 — S1 10 dk/25 dk, otobüs 292, taksi durakları, gece otobüsü 606 satırı
2. https://www.hamburg-airport.de/de/unternehmen/presse/start-in-die-maerzferien-85890 — S1 istasyon erişimi, 292 hattı
3. https://www.hvv.de/resource/blob/153742/b92fe2832ff6a542c0ab00926d92b1a4/PM251028_Tarifanpassung.pdf — hvv 2026 tarife bildirisi (Einzelkarte 4,10 €, online 3,81 €, %7 indirim)
4. https://www.hamburg.de/verkehr/bus-bahn/s-bahn/s1-410978 — S1 işletme ~04:00–01:00, hafta sonu gece boyunca, Ohlsdorf'ta bölünme
5. https://www.hvv.de/en/tickets/single-day-tickets — hvv Einzel/Tageskarte 2026 fiyatları
6. https://www.hamburg-airport.de/de/anreisen-parken/parken/uebersicht/faq-haeufig-gestellte-fragen-taxi-53678 — taksi SSS (durak, ödeme, ön rezervasyon/sabit fiyat)
7. https://www.hamburg.de/politik-und-verwaltung/behoerden/bvm/die-themen-der-behoerde/fuer-taxi-fahrgaeste/taxi-fahrpreise-410302 — Hamburg taksi tarifesi (4,50 / 2,70 / 2,00 €; bekleme 38 €/sa)
8. https://www.hamburg.de/politik-und-verwaltung/behoerden/bvm/1013322-1013322 — ön rezervasyonlu sabit fiyatlar (38/52/82 €)
9. https://www.hvv.de/resource/blob/138986/31f4981ab4725cb11a55cbbff023266f/PM241105_Tarifanpassung_Website.pdf — 9-Uhr-Tageskarte'nin kaldırılması
10. https://www.hvv.de/de/tickets/weitere-tickets/wochen-monatstickets — Gesamtnetz Wochenkarte 43 €
11. https://www.hamburg.de/verkehr/hvv/hvv-any-410900 — hvv Any check-in / gün sonu en ucuz bilet
12. https://www.hamburg-tourism.de/card — Hamburg CARD fiyatları ve kapsam
13. https://www.hvv.de/de/tickets/weitere-tickets/hamburgcard — Hamburg CARD (hvv), 12,90 €'dan, satış noktaları
14. https://www.hamburg-travel.com/booking/hamburg-card/ — Hamburg CARD from €12.90
15. https://www.bahn.de/angebot/regio/deutschland-ticket — Deutschland-Ticket 63 €, abonelik, 2027 fiyatı
16. https://www.antalya-airport.aero/passengers-visitors/transportation-parking/taxis — AYT taksi durakları, ücret panosu, D400 ~20 dk
17. https://www.bahn.de/faq/pk/angebot/regionale-angebote/deutschland-ticket — ay ortası alım, 10'u kuralı
18. https://www.bahn.de/faq/pk/service/buchung/bezahlen — ödeme yöntemleri (kredi kartı 3D Secure, PayPal, SEPA)
19. https://stadtrad.hamburg.de/en/prices — StadtRAD tarifeleri (EN)
20. https://stadtrad.hamburg.de/de/registrieren?tariff=1000000781 — StadtRAD tarifeleri (DE)
21. https://hadag.de/en/routes/62/ — hat 62, hvv bileti geçerli
22. https://www.hamburg.de/verkehr/hadag-linie-62-314160 — hat 62 sıklık/duraklar
23. https://antalyakenthaber.com/antalya-taksi-ucretleri-2026-acilis-kilometre-ve-kisa-mesafe-tarifesi-32735 — Antalya taksi 2026 (40/50/200 TL)
24. https://www.yenialanya.com/alanya-ve-antalya-taksi-tarifesi-tartismasina-resmi-yanit — UKOME kararı 23 Mart 2026, bekleme 240 TL/sa
25. https://www.antalyaulasim.com.tr/Hizmetlerimiz/Antray — ANTRAY kuralları, "Hareket Saatleri" bölümü
26. https://www.antalyaulasim.com.tr/Bildirim/YolcuRehberi — sefer saatleri bağlantısı, çağrı merkezi 0242 606 07 07
27. https://tr.wikipedia.org/wiki/T1_(Antalya_tramvay%C4%B1) — T1 durak listesi (Meydan, Sinan, Yonca Kavşak, Havalimanı Gidiş/Geliş)
28. https://guncelantalya.com/antalyada-ulasima-6-yilda-yuzde-1352-zam-indi-bindi-icin-istenilen-fiyat-belli-oldu — tam bilet 42 TL (Mart 2026), 53 TL talebi (9 Ekim 2026)
29. https://www.e-yasamrehberi.com/havaalani_otobus/antobus-600-otogar-antalya-havalimani-otobus-saatleri.html — 600 hattı (üçüncü taraf)
30. https://www.antalya-airport.aero/help — T1 24 saat taksi SSS
31. https://www.turkishairlines.com/en-de/any-questions/check-in/ — THY check-in kapanış 60 dk, 3 sa önerisi
32. https://www.flypgs.com/en/useful-info/info-about-flights/check-in — Pegasus 60 dk
33. https://www.sunexpress.com/en-gb/information/passenger-info/check-in/ — SunExpress 60 dk, HAM online check-in 72 sa–1 sa
34. https://regional.bahn.de/regionen/schleswig-holstein/fahrplan/fahrplandownload — RE8/RE80 tarife tabloları, inşaat uyarıları
35. https://www.bahn.de/reisen/view/verbindung/hamburg/luebeck.shtml — en hızlı 43 dk, günde ~40 bağlantı
36. https://unternehmen.nah.sh/assets/Pressemitteilungen-PDF/2026-02-05-NSH_PI_Tarifanpassung_SH-Tarif_2026.pdf — SH-Tarif 1 Nisan 2026: Hamburg–Lübeck Einzelkarte 18,90 €, Tageskarte 35,40 €
37. https://www.nah.sh/assets/01_NSH/26-04-01_Tarifbestimmungen_Schleswig-Holstein-Ticket_online.pdf — SH-Ticket tarife şartları
38. https://www.bahn.de/angebot/regio/laender-tickets/schleswig-holstein-ticket — SH-Ticket 34 € ve saat kuralı
39. https://www.hamburg-airport.de/en/depart-arrive/check-in-metanavi-en/check-in-overview — check-in genel bakış, 2 sa önerisi
40. https://www.hamburg-airport.de/de/unternehmen/presse/ferien-im-norden-hamburg-airport-ist-gut-vorbereitet-80232 — tatil döneminde en az 2 sa
41. https://www.hamburg-airport.de/en/depart-arrive/check-in-metanavi-en/self-bag-drop ve https://www.hamburg-airport.de/en/depart-arrive/check-in-metanavi-en/late-night-check-in — Self Bag Drop, bir önceki akşam check-in
42. https://hha-prod-waf.cms.hamburg-airport.de:8443/blueprint/servlet/de/abfliegen-ankommen/check-in-metanavi/slot-and-fly — Slot&Fly
43. https://www.hamburg.de/verkehr/hvv/hvv-preiserhoehung-410930 — hvv 2026/2027 fiyat tablosu (Tageskarte 8,20 / 7,63 €, Wochenkarte 43 €)
44. https://www.nah.sh/de/themen/neuigkeiten/sh-tarif-2026/ — SH-Tarif 2026 değişiklikleri

## Açık noktalar / kullanıcı kararı gereken
1. **Arama bütçesi doldu:** 13 Aralık 2026 tarife değişikliğinin (DB Fahrplanwechsel) RE8/RE80 ve S1 saatlerine etkisi sorgulanamadı; dönüş günü için bahn.de/hvv app'ten yeniden bakılmalı.
2. **Uçuş saatleri** gelince: gece/gündüz senaryolarından biri silinecek; HAM gece varışında taksi (~35 €) bütçeye eklenecek; Antalya erken sabah kalkışında taksi zorunlu.
3. **Deutschlandticket iptal disiplini:** alım ≤10 Aralık ve iptal ≤10 Aralık; unutulursa +66,80 €. Yurt dışı kredi kartıyla abonelik akışı (3D Secure) kullanıcı tarafından denenmeli.
4. **Wochenkarte** (43 €) 7 Aralık'tan başlatılabiliyor mu, aktarılabilir mi — hvv switch app'te kontrol.
5. **Hamburg CARD** fiyatı (12,90 vs 11,90 € seti) ve Aralık 2026 geçerliliği satın alma anında teyit; müze planı netleşmeden alınmamalı.
6. **Antalya:** Güvenlik Mh.→AYT km ve en yakın AntRay durağı bulunamadı (harita ile teyit); 12 Ekim 2026 meclis zam kararı sonucu (42→53 TL?) ve UKOME taksi tarifesinin Aralık'ta hâlâ geçerli olup olmadığı doğrulanmalı; Havaş ücreti/saati bulunamadı.
7. **HAM gece otobüsü 606** havalimanına uğruyor mu — hvv app'ten; aksi hâlde gece varışında taksi.
8. **Feribot 62 kış tarifesi** (2 Kasım 2026 sonrası) — hvv app.
9. **Kur:** TRY tutarları EUR'ya çevrilmedi (kur kaynağına erişilemedi); orkestratör bütçe toplamı için kur ekleyecek.
