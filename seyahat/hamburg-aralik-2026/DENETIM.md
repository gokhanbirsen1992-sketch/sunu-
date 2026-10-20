# DENETİM — Hamburg Turu Planı (7–13 Aralık 2026)

**Denetim damgası:** 2026-10-20 · Denetlenen: `PLAN.md`, `01-ucus.md`, `02-otel.md`, `03-transfer-ulasim.md`, `04-gezi-programi.md`, `05-belge-pratik.md`, `hesap/butce-kalemleri.json`, `hesap/butce-tablo.md`.
**Yöntem/ortam:** `WebFetch` tek denemede `ENOTFOUND` (tuerkei.diplo.de) → hiçbir sayfa doğrudan açılamadı. Kaynak doğrulaması yalnız `WebSearch` ile (28 sorgu, önce `site:` kısıtlı, bulunamayanlar için serbest). "Doğrulandı" = resmî alan adından dönen arama özetinde iddia birebir geçiyor. Bütçe, kur çevrimi, tarih/gün ve saat zincirleri python ile yeniden hesaplandı (`scratchpad/denetim_hesap.py`). Hiçbir plan dosyası değiştirilmedi; düzeltmeler §7'de.

## Özet
- 28 iddia denetlendi: **14 doğrulandı**, 4 kısmen, **9 doğrulanamadı** (etiket düşürüldü, iddia silinmedi), 1 araç çıktısı (aramayla doğrulanamaz).
- Bütçe toplamları, 5 senaryo, USD→EUR (1,1225) ve TRY (55,6227) çevrimleri, 04 §7 bilet toplamları ve 03 bilet karşılaştırması **birebir tutuyor**; tarih/gün hesapları (ISO 50. hafta, 13/20/22 Kas, Totensonntag, Advent cumartesileri, gün ışığı) doğru.
- Saat zincirleri tutarlı (12:45 iniş → 14:15 otel → 15:00 oda; 19:10 kalkış ← 16:20 otel çıkışı; Fischmarkt 07:00–09:30 → 09:30 check-out); Gün 7 tablosunda sunum çelişkisi var (§4).
- **1 kırmızı bayrak:** vize randevusu olmadan planın tamamı uygulanamaz; iade edilemez rezervasyon yapılmamalı.
- Uydurma bulunmadı; kaynaksız load-bearing sayı yok. Ancak `[kesin]` etiketli 9 iddia erişilebilir resmî kaynakta birebir bulunamadı → `[doğrulanmalı]`.

---

## 1. Kaynak denetimi tablosu

| # | Dosya | İddia | Etiket (eski→yeni) | Kaynak doğrulandı mı | Not |
|---|---|---|---|---|---|
| 1 | 05 §1, PLAN §0 | iDATA Almanya için **tek yetkili** dış hizmet sağlayıcı; aracıların randevu erişimi yok | [kesin] → [kesin] | **Evet** — tuerkei.diplo.de iDATA vekâletname PDF'i: "tek resmî yetkili kurum"; İzmir Başkonsolosluğu notu: aracıların vize bölümüyle bağı yok | Bekleme listesi sayfası (1698328) aramada dönmedi (bkz. #4) |
| 2 | 05 §1, PLAN §0 | Vize ücreti **90 €** | [kesin] → [kesin] | **Evet** — tuerkei.diplo.de PDF: "Vize Ücreti: 90 EUR" | PDF'in bir sürümü 80 € (eski) |
| 3 | 05 §1, PLAN §0/§7 | iDATA hizmet bedeli **39,92 €** (+12 € randevu bedeli) | [kesin] → **[doğrulanmalı]** | **Hayır** — tuerkei.diplo.de PDF'inde koordinasyon bedeli **32,81 €** (tarihsiz); idata.com.tr aramada dönmedi; üçüncü taraflar 30/40/50 € ve "randevu ücretsiz" diyor. 39,92 ve 12 € hiçbir sonuçta yok | Bütçe etkisi ±7–19 €; iDATA ofisinde TL tutar ödenir |
| 4 | 05 §1, PLAN §0 | Bekleme süresi "birkaç aydan yaklaşık bir yıla" (resmî sayfa) | [doğrulanmalı] → [doğrulanmalı] | **Hayır** — ifade birebir bulunamadı (arama özeti yetersiz). Bağımsız kaynaklar: 1–7 ay (acente), 5–6 ay (acente), "birkaç haftadan birkaç aya" (Ankara Büyükelçiliği açıklaması, haber) | Tüm kaynaklar aylar mertebesinde → §2 K1 |
| 5 | 05 §1, PLAN §0 | İşlem süresi **15 gün**, istisnai **45 gün** | [kesin] → **[doğrulanmalı]** | **Hayır** — tuerkei.diplo.de SSS sayfası aramada dönmedi; 15/45 AB Vize Kodu md. 23 standardı (um.dk Danimarka sayfası aynı) → içerik doğru, atıf doğrulanamadı | Çizelge (13/20/22 Kas) bu süreye dayanıyor; süre AB hukukundan geldiği için çizelge geçerli |
| 6 | 05 §1 | Pasaport: son 10 yılda düzenlenmiş, dönüşten ≥3 ay geçerli, 2 boş sayfa | [kesin] → **[doğrulanmalı]** | **Hayır** — aynı SSS sayfası dönmedi; üçüncü taraf "≥90 gün" doğruluyor, "10 yıl" kuralı bulunamadı | AB Vize Kodu md. 12 ile uyumlu; 13.03.2027 hesabı doğru |
| 7 | 03 §3, PLAN §1/§4 | hvv Einzelkarte AB **4,10 €** / app **3,81 €** (%7) | [kesin] → [kesin] | **Evet** — hvv.de PM251028: "4,10 Euro", "%7 online indirim → 3,81" | 4,10×0,93 = 3,81 ✓ |
| 8 | 03 §3, 04 §2 | hvv Tageskarte AB **8,20 €** (app 7,63) | [kesin] → [kesin] | **Evet** — hamburg.de hvv 2026 tablosu: 8,20 € ("ohne Gewähr") | hvv.de'nin kendi sayfası dönmedi; 8,20×0,93 = 7,63 ✓ |
| 9 | 03 §2, PLAN §4 | S1 HAM⇄Hbf **25 dk**, **10 dk'da bir** | [kesin] → [kesin] | **Evet** — hamburg-airport.de: "every 10 minutes … only 25 minutes each way" | — |
| 10 | 04 §1, PLAN §5 | Rathausmarkt Noel pazarı **23 Kas–23 Ara 2026** | [kesin] → [kesin] (tarih) | **Evet** — hamburg.de resmî sayfa: 23.11.–23.12.2026 | 02-otel'deki [doğrulanmalı] etiketi [kesin]'e yükseltilebilir |
| 11 | 04 §1, PLAN §5 | Rathausmarkt **her gün 11–21** | [kesin] → **[doğrulanmalı]** | **Kısmen** — hamburg.de özetinde saat yok; 11–21 yalnız üçüncü taraf (festivalsindeutschland) | Gün 1 planı 15:00–16:00 için risk yok |
| 12 | 04 §1, PLAN §5 | Santa Pauli **9 Kas–23 Ara 2026**, Çar 16–23, Cts 13–01 | [kesin] → [kesin] | **Evet** — hamburg.de: 9.11.–23.12.2026; saatler festivalsindeutschland | hamburg.de başlığında hâlâ 2025 tarihi var |
| 13 | 04 §1, PLAN §5 | HafenCity Noel pazarı **16 Kas–30 Ara 2026** | [kesin] → **[doğrulanmalı]** | **Hayır** — tarih aralığı hiçbir sonuçta geçmedi (arama özeti yetersiz) | Gün 2 16:30 ziyareti için 2025 saatleri (Sa 15–20) zaten [doğrulanmalı] |
| 14 | 04 §2, PLAN §5 | Fischmarkt **15 Kas–14 Mar Pazar 07:00–09:30** | [kesin] → [kesin] | **Evet** — hamburg.de Bezirk Altona: "Vom 15. November bis 14. März: 7:00 Uhr bis 9:30 Uhr" | Bürgerschaft "geç başlangıç" incelemesi (Mayıs 2026) açık nokta olarak kalır |
| 15 | 04 §2, PLAN §5 | Elbphilharmonie Plaza **5 €**, 5 Ekim 2026'dan | [kesin] → [kesin] | **Evet** — elbphilharmonie.de Plaza sayfası: "ab dem 5. Oktober 2026 … 5 Euro"; indirimli 3 € | Haber: Bürgerschaft bütçe onayı bekleniyor, tarih yine de uygulanıyor |
| 16 | 04 §2, PLAN §5/§6 | Miniatur Wunderland **22 €** | [doğrulanmalı] → [doğrulanmalı] | **Kısmen** — miniatur-wunderland.de dönmedi; hamburg-tourism.de "ab 22,00 €" (zaman dilimli) | Üçüncü taraflar 22–25 €; 04 etiketi zaten doğru |
| 17 | 03 §4, 04 §2, PLAN §4 | Schleswig-Holstein-Ticket **34 €**, hafta içi **09:00**–03:00 | 03/PLAN [kesin], 04 [doğrulanmalı] → **[kesin]** | **Evet** — bahn.de: "ab 34 Euro … 1 Reisender", "von 9 Uhr bis 3 Uhr des nächsten Tages"; gişe +2 € | 04'teki etiket yükseltilebilir |
| 18 | 03 §3, PLAN §4 | Deutschlandticket **63 €/ay**; **10'una kadar** iptal → ay sonu biter | [kesin] → [kesin] (kural) / **[doğrulanmalı]** (fiyat) | **Evet** kural (bahn.de: "bis zum 10. … endet am Ende des laufenden Monats"); fiyat 63 € birden çok bahn.de sayfasında, ancak bir SSS "1 Temmuz 2026'dan yeni fiyat" ibaresi içeriyor (özet belirsiz) | 2027 fiyatı 66,80 € doğrulanmadı; satın alırken uygulamadaki fiyatı gör |
| 19 | 05 §5, PLAN başlık/§7, hesap/ | ECB 19.10.2026: **1 € = 1,1225 USD = 55,6227 TRY** | [kesin] → **[doğrulanmalı]** | **Hayır** — ecb.europa.eu 19.10 bülteni aramada yok; en yeni ECB sonucu 01.07.2026 (USD 1,1383, TRY 53,1266), üçüncü taraf 19.08.2026 EUR/USD 1,1605 | Değerler 02-otel (13.10: 1,1188/55,2325, Banca d'Italia) ve TCMB 02.10 çaprazı (1,1248) ile tutarlı → uydurma değil; etki ±1 % |
| 20 | 05 §1, PLAN §8 | EES HAM'da **02.12.2025**'ten itibaren; kiosk + yüz + parmak izi | [kesin] → [kesin] | **Evet** — hamburg-airport.de pasaport kontrol sayfası: "New from December 2, 2025" | ~15 dk kuyruk [doğrulanmalı] olarak kalır |
| 21 | 02 check-in tablosu, PLAN §3/§5 | Lindner Am Michel check-out **Pazar 14:00** (Pzt–Cts 11:00) | [kesin] → **[doğrulanmalı]** | **Hayır** — hyatt.com SSS aramada dönmedi; Expedia/Hotels.com/Booking: check-out 11:00, geç çıkış "müsaitliğe bağlı, ücretli"; Pazar istisnası hiçbir sonuçta yok | Gün 7 planı 09:30'da çıkış yaptığı için program etkilenmez |
| 22 | 03 §2, PLAN §4 | Hamburg taksi **4,50 € + 2,70 €/km** (<9 km), 2,00 €/km (>9 km); sabit 38 € | [doğrulanmalı] → [doğrulanmalı] | **Kısmen** — hamburg.de dönmedi; taxi-times (Senat tarife reformu 01.02.2025) ve taxirechner.de aynı rakamları veriyor | 11–13 km hesabı 32,8–36,8 € ✓ |
| 23 | 01 Tablo 1, PLAN §1/§2 | XQ170 7 Ara **10:40→12:45**; XC151 13 Ara **19:10→01:10** | [kesin] → [kesin] (araç çıktısı) | **Araç çıktısı** (SlickTrip, 7 Ara 2026 için canlı). Çapraz kontrol: flightmapper 10:40→12:45'i **kış 2025/26** (–28.03.2026) tarifesi olarak listeliyor; yaz 2026 tarifesi 07:00→09:55; Aralık 2026 satırı yok | Kış tarifesi döndüğünde 10:40 slotu tutarlı; rezervasyonda teyit. Saat 07:00'ye kayarsa Gün 1 ve Antalya taksisi (03:20 çıkış) baştan planlanmalı → §3 S1 |
| 24 | 02, PLAN §3 | Lindner 954 USD / CAB20 442 / MADISON 1.357 USD | [kesin] → [kesin] (araç çıktısı) | Araç çıktısı; aramayla doğrulanamaz; satıcı linkleri 1 gün geçerli | Fiyat anlık, 20.10 damgalı ✓ |
| 25 | 04 §2, PLAN §5 | Hamburger Kunsthalle **18 €**; Pzt kapalı; Per 21:00'e kadar | [kesin] → **[doğrulanmalı]** (fiyat) / [kesin] (gün/saat) | Gün/saat **Evet** (kunstmeile-hamburg.de, thebettervacation); fiyat **Hayır** — üçüncü taraf 16 €; hamburger-kunsthalle.de dönmedi | Bütçe etkisi ≤2 € |
| 26 | 04 §2, PLAN §5/§7 | Dialog im Dunkeln **ab 18,50 €**; Pzt kapalı | [kesin] → **[doğrulanmalı]** | Pzt kapalı **Evet** (hamburg.de branchenbuch, bozuk kayıt); fiyat: rausgegangen.de yetişkin **24,50 €**, indirimli 20,50, çocuk (≤13) **18,50 €** → "ab 18,50" çocuk fiyatı olabilir | Bütçede yetişkin kalemi 18,50 → muhtemelen 24,50 € (+6 €) |
| 27 | 04 §2, PLAN §5 | Lübeck Weihnachtsstadt **23 Kas–30 Ara 2026**; Traditioneller Markt Pzt–Per 11–21 | [kesin] → **[doğrulanmalı]** | **Kısmen** — luebeck-tourismus.de dönmedi; festivalsindeutschland 23.11.–30.12.2026; saatler 2025 verisi | Gün 4 (Per 10 Ara) için açık gün/saat uyumlu |
| 28 | 03 §1, PLAN §4/§7 | Antalya taksi UKOME 2026: açılış **40 TL + 50 TL/km**, indi-bindi 200 TL | [doğrulanmalı] → [doğrulanmalı] | **Hayır** — resmî UKOME kararı bulunamadı; kaynaklar çelişkili (hemenhesap 50/50/200; transfer siteleri 60/70 veya 40/60) | Üst sınır 840 TL/yön makul; 2×840 = 30,20 € ✓ |

**Doğrulanmayan ama denetlenmeyen `[kesin]`'ler (kota/öncelik dışı):** UKE iletişim bilgileri (PLAN §5), T.C. Hamburg Başkonsolosluğu telefonları (PLAN §8), Rathaus turu 8 €/saat başı, EisArena 15+10 €, Maritimes Museum 18/9 €, Chocoversum 23 €, Speicherstadtmuseum 5 €, Rickmer Rickmers 7 €, Michel kulesi 8 €, Bundesbank %45 nakit, Pfand 0,25 €. Bunlar alt raporlarda resmî alan adına atıflı; etiketleri korundu, "bugün görüldü" şartı arama özetiyle karşılanmış sayıldı.

---

## 2. Kırmızı bayraklar (düzeltilmeden plana güvenilmez)

**K1 — Vize randevusu planın ön koşulu; mevcut değilse 7–13 Aralık tarihi uygulanamaz.** PLAN §0 bunu doğru kuruyor, ancak §6 takviminde "20–27 Eki uçuş/otel kararı" satırı vize durumu netleşmeden rezervasyona yönlendiriyor. Resmî bekleme süresi ifadesi doğrulanamadı; erişilen her kaynak (acenteler, Büyükelçilik açıklaması) **aylar** mertebesi veriyor. Kullanıcı (a) yeşil pasaport, (b) geçerli çok girişli vize veya (c) tarihli randevu bildiriminden birini teyit etmeden **iade edilemez hiçbir rezervasyon** (Lindner 954 USD Super.com, XQ170/XC151 ayrı biletler) yapılmamalı; §6'daki "20–27 Eki" satırı "vize teyidi sonrası" diye koşullanmalı. Yeşil pasaport muafiyeti de 05'te `[doğrulanmalı]` (kaynak staj/araştırma bağlamlı) — mfa.gov.tr veya tuerkei.diplo.de genel sayfasından teyit şart.

Başka kırmızı bayrak yok: kaynaksız load-bearing sayı veya uydurma bulunmadı; bütçe ve saat zincirleri hesapla tutuyor.

---

## 3. Sarı bayraklar (kullanıcı teyit etmeli)

| # | Konu | Neden | Ne yapmalı |
|---|---|---|---|
| S1 | **Uçuş saatleri mevsimsel** (#23) | XQ170 10:40 slotu kış 2025/26 tarifesine ait; yaz 2026'da 07:00. Aralık 2026 için araç 10:40 veriyor ama yayımlı tarife satırı görülmedi | SunExpress sitesinde 7 Ara saatini teyit et; 07:00 çıkarsa Antalya taksisi ~03:20, HAM varış 09:55, otel 15:00'e kadar valiz emaneti |
| S2 | **iDATA 39,92 € + 12 €** (#3) | Resmî PDF 32,81 € (tarihsiz); 39,92 hiçbir kaynakta yok | iDATA ofisinde/çağrı merkezinde güncel TL tutarı sor; bütçe 129,92 → 122,81–141,92 € aralığı |
| S3 | **ECB 19.10 kuru** (#19) | Sayfa açılamadı; değer tutarlı ama birebir görülmedi | Rezervasyon günü ECB/TCMB kurunu yeniden çek; tüm EUR/TRY sütunları ±1 % oynar |
| S4 | **Alt rapor kurları ≠ PLAN kuru** | 01-ucus "≈EUR" sütunu 1,1210 (hisse.net 14.10) ile: 213 USD → ~190 €; 02-otel 1,1188 (ECB 13.10) ile: 954 USD → 853 €; PLAN 1,1225 ile 189,76 / 849,89 €. PLAN'ın **tüm** USD→EUR değerlerini ECB 19.10 ile yeniden hesapladığı python ile teyit edildi (14 değer birebir) | Hata değil, kur farkı (≤0,4 %). Alt raporlar okunurken PLAN rakamı esas alınmalı |
| S5 | **Lindner Pazar 14:00 check-out** (#21) | Üçüncü taraflar 11:00; Pazar istisnası görülmedi | Rezervasyonda sor; plan 09:30 çıkış + valiz emaneti ile zaten uyumlu |
| S6 | **Dialog im Dunkeln yetişkin fiyatı** (#26) | "ab 18,50" muhtemelen çocuk fiyatı; yetişkin 24,50 € | Bütçe müze kalemi 142,50 → 148,50 €; genel toplam +6,60 € (yedek dâhil) |
| S7 | **Kunsthalle 18 € vs 16 €** (#25) | Resmî sayfa görülmedi | Gişede/online bak; etki ≤2 € |
| S8 | **Deutschlandticket fiyatı** (#18) | bahn.de SSS'de "1 Temmuz 2026'dan yeni fiyat" ibaresi (özet belirsiz); 2027 66,80 € doğrulanmadı | DB Navigator'da abonelik ekranındaki fiyatı gör; 63 €'dan yüksekse hvv+SH-Ticket (79,10 €) ile karşılaştır |
| S9 | **Rathausmarkt 11–21 saatleri**, **HafenCity 16 Kas–30 Ara**, **Lübeck 2026 tarihleri** (#11, #13, #27) | Yalnız üçüncü taraf | Aralık başında hamburg.de / luebeck-tourismus.de |
| S10 | **Liman turu Çarşamba kış seferi** (04 §2) | Abicht kışın yalnız hafta sonu olabilir; Barkassen-Meyer her gün | 9 Ara iskelede kontrol; yedek HADAG 62 |
| S11 | **Antalya ev→AYT çıkış saati çelişkisi** | 01-ucus: "en geç 08:30 (2 saat önce)"; 03/PLAN: 07:00–07:30 (3 sa + 25 dk) | PLAN'ın 07:00–07:30'u esas (kontuar 09:40'ta kapanır); 01'deki 08:30 ibaresi düzeltilmeli |
| S12 | **Antalya taksi tarifesi** (#28) | UKOME kararı doğrudan görülmedi; üç farklı rakam seti | Araçtaki tarife levhası; bütçe üst sınır 840 TL/yön yeterli tampon |
| S13 | **Yeşil pasaport muafiyeti** (PLAN §0) | 05'te [doğrulanmalı]; PLAN §0 hücresinde etiketsiz | Hususi pasaport varsa mfa.gov.tr/tuerkei.diplo.de'den 90 gün muafiyetini teyit et |
| S14 | **UKE iletişim ve Başkonsolosluk telefonları** | Arama özetinden, bu denetimde doğrulanmadı | Aramadan önce resmî sayfadan kontrol |
| S15 | **Fischmarkt saat değişikliği** | Bürgerschaft Mayıs 2026 incelemesi; uygulanan değişiklik yok (bugün) | Aralık başında Bezirksamt Altona sayfası |

---

## 4. Tutarlılık bulguları

**4.1 Uçuş varış ↔ otel check-in** — 12:45 iniş + 45 dk (bagaj/EES) + 25 dk S1 + ~20 dk yürüyüş/aktarma = **14:15** otel (PLAN §3) ✓; check-in 15:00 → valiz emaneti doğru. Küçük farklar: 04 Gün 1 tablosu "14:30 Otel **check-in**" yazıyor (15:00 kuralına aykırı; PLAN düzeltmiş) ve "15:00 oda → 15:00–16:00 Rathausmarkt" aynı saatte (16 dk yürüme) — gün batımı 16:01 olduğundan "gün ışığında Rathaus cephesi" için 15:20'de yola çıkılmalı. Sunum düzeyinde, program bozulmuyor.

**4.2 Dönüş kalkış ↔ Fischmarkt ↔ check-out ↔ transfer** — Fischmarkt Pazar 07:00–09:30 (doğrulandı) → 07:00–08:30 ziyaret → 09:30 check-out (11:00 standardının altında; Pazar 14:00 doğrulanmasa da sorun yok) → 19:10 kalkış için otelden en geç **16:20** (19:10 − 2 sa 50 dk ✓ hesap) → terminalde 17:10 ✓. **Çelişki (sunum):** PLAN §5 Gün 7 ve 04 Senaryo A tablosu "14:30–15:00 Hbf → HAM (S1) → 17:10 terminal" diyor; S1 14:30'da binilirse terminal ~15:00–15:25'tir, 17:10 ise "en geç" eşiğidir. İki farklı mantık aynı satırda. Önerilen tek satır: "15:30 otelden valiz al → 16:00 S1 (Stadthausbrücke) → 16:35 HAM → 17:10'dan önce terminal". Ayrıca Gün 7'de 3 hvv binişi var (otel→Fischmarkt, Fischmarkt→otel valiz, otel→HAM) ama 04 §7 yalnız 2 Einzelkarte (8,20 €) bütçelemiş; 3×4,10 = 12,30 € yerine Tageskarte 8,20 € alınırsa bütçe değişmez (79,10 € kalır), Einzelkarte ile +4,10 € olurdu. Hata değil, bilet türü notu. XQ171 (13:35) senaryosu: Fischmarkt 07:00–08:15 → 09:30 S1 → 10:15 terminal ✓ (13:35 − 2 sa = 11:35 eşiği).

**4.3 Lübeck günü (Per 10 Ara) ↔ SH-Ticket ↔ pazar günleri** — SH-Ticket hafta içi 09:00'dan (bahn.de doğrulandı) → 09:05 RE8 ✓; Lübeck 09:50 → Holstentor 10:00, Märchenwald (Pzt–Cts 10–19:30) 10:30 ✓, Traditioneller Markt (Pzt–Per 11–21) 11:30 ✓, St. Petri Kunsthandwerkermarkt (24 Kas–20 Ara) ✓, Koberg (23 Kas–29 Ara) ✓; Heiligen-Geist-Hospital (–6 Ara) doğru şekilde dışlanmış. 10 Ara, 13 Ara DB tarife değişikliğinden önce ✓. Lübeck Hbf–Büchen kapanışı (19 Eki–12 Ara) Hamburg hattını etkilemiyor (03 [doğrulanmalı]). Akşam Kunsthalle Perşembe 21:00 (doğrulandı) → 17:45 Hbf varış + 18:30 giriş ✓.

**4.4 Pazartesi kapalı yerler ↔ program** — Kunsthalle (Pzt kapalı, doğrulandı) → Per 10 veya Cu 11 Ara ✓; Dialog im Dunkeln (Pzt kapalı, doğrulandı) → Cu 11 Ara 14:30 ✓. Gün 1 (Pzt) yalnız pazarlar + yemek ✓. Gün 6 Cts: 12:45–14:00 Fischereihafen (Altona) öğle ile 14:00 Roncalli paradesi (Mönckebergstraße) çakışıyor → 17:00 paradesi seçilmeli. Gün 3: Cap San Diego 14:30–15:30 → Michel kulesi 15:15 çakışma (15 dk) — Cap San Diego "isteğe bağlı/zaman kalırsa" işaretli ✓.

**4.5 Bütçe (python yeniden toplama)** — `butce-kalemleri.json` 9 kalem: **1.755,28 €** ara toplam ✓, yedek **175,53 €** ✓, genel **1.930,81 €** ✓; TRY 97.633 / 9.763 / 107.397 ✓ (55,6227). PLAN §7 tablosu ve `butce-tablo.md` birebir. Senaryolar: CAB20 1.429,07 ✓ · Lindner iptalli 2.186,58 ✓ (yuvarlanmış 1.082,41 ile) · MADISON 2.325,73 ✓ · MADISON iptalli 2.605,02 ✓. USD→EUR/1,1225: 213→189,76 ✓ · 954→849,89 ✓ · 442→393,76 ✓ · 1.357→1.208,91 ✓ · 1.215→1.082,41 ✓ · 1.642→1.462,81 ✓ · 247→220,04 ✓ · 673→599,55 ✓ · 10→8,91 ✓. THY 19.121,77 TRY → 343,78 € ✓ (01'deki ~345 € = 55,40 kuru). Ücretsiz iptal primi 1.215−954 = 261 ✓, 1.642−1.357 = 285 ✓. Taksi 2×840/55,6227 = 30,20 ✓. Vize 129,92 → 7.227 TRY ✓. 04 §7: çekirdek 142,50 ✓, ulaşım 79,10 ✓ (3×4,10 + 4×8,20 + 34), genel 221,60 ✓, isteğe bağlı 147,90 ✓, üst sınır 369,50 ✓, D-Ticket tasarrufu 16,10 ✓, Hamburg CARD 97,80 ✓. 03 bilet tablosu A 87,41 / B 77,00 / C 63,00 / D 104,16 ✓; CARD primi 3,35 €/gün ✓. Taksi HAM 11–13 km: 32,8–36,8 € ✓. **Bulgu:** bütçe S6 ile +6 € (Dialog), S2 ile −7/+12 € (iDATA) oynar; Gün 7 için Tageskarte alınmazsa +4,10 € (bkz. 4.2).

**4.6 Tarih/gün hesapları** — 7 Ara Pzt, 13 Ara Paz, ISO 50 ✓; 10 Ara Per ✓; 13 Kas Cu (T-24), 20 Kas Cu (T-17), 22 Kas Paz (T-15), 23 Eki Cu (T-45), bugün T-48 ✓; 13 Kas + 15 gün = 28 Kas ✓; pasaport ≥13.03.2027 ✓; 1. Advent 29 Kas → Totensonntag 22 Kas ✓; Advent cumartesileri 28 Kas/5/12/19 Ara ✓ (12 Ara parade günü). Gün ışığı NOAA yeniden hesabı 7 Ara 08:21/16:02, 13 Ara 08:28/16:01 — rapor ±1 dk ✓. Saat farkı 2 sa (TR UTC+3, DE UTC+1) ✓.

**4.7 Çapraz rapor çelişkileri** — (a) 01 "evden 08:30" vs 03/PLAN "07:00–07:30" (S11). (b) 02 Rathausmarkt [doğrulanmalı] vs 04 [kesin] → tarih için [kesin] (doğrulandı). (c) 04 SH-Ticket 09:00 [doğrulanmalı] vs 03/PLAN [kesin] → [kesin] (doğrulandı). (d) 04 "otelde ~14:30" vs PLAN "~14:15" — önemsiz. (e) 03 "HAM gece varışı taksi" senaryosu 12:45 inişle geçersiz; PLAN doğru şekilde atlamış. (f) 05 §7 şablonu "S1 ~3,80 €" vs 03 3,81 € — önemsiz.

---

## 5. Boşluk denetimi

**5.1 "Bulamadım / bulunamadı / doğrulanamadı" geçişleri (dosya bazında):**
- **01-ucus:** TCMB 20.10 kuru; SlickTrip biletlerinin tarife sınıfı (Light/Eco) ve bagaj ücreti; 6 Ara→12 Ara kombinasyonu sorgulanmadı.
- **02-otel:** MADISON bagaj depolama; ECB 20.10 kuru; semt yürüme süreleri resmî haritayla doğrulanamadı; CAB20 "Flex Rate" iptal koşulu.
- **03-transfer:** S1 ilk/son tren dakikası; gece otobüsü 606 havalimanı; HAM resmî taksi ücret tahmini; Havaş Antalya ücret/saat; AntRay Meydan→Havalimanı süresi ve resmî sefer aralığı; Güvenlik Mh.'ye en yakın AntRay durağı; Güvenlik Mh.→AYT km; Antalya 12 Eki 2026 zam kararı sonucu; Wochenkarte 7 gün başlangıç kuralı; hvv Any günlük tavan; Hamburg CARD fiyat seti (12,90 vs 11,90); HAM pasaport kontrol bekleme süresi; feribot 62 kış tarifesi; 13 Ara DB tarife değişikliği etkisi (arama kotası doldu); yabancı kartla D-Ticket aboneliği.
- **04-gezi:** Elbphilharmonie 11 Ara programı; Holstentor müze ücreti; Lübeck St. Petri kule ücreti; Buddenbrookhaus yenileme durumu; DWD 1991–2020 Aralık normali (PDF açılamadı); Fleetschlösschen adresi; Daniel Wischer kesin adresi; timeanddate sayfası; Brücke 10 menü fiyatı; Hamburg Dungeon/Panoptikum fiyatı (sorgulanmadı); vejetaryen mekân adresleri (sorgulanmadı); helal et kaynağı yok; Rathaus turu 11 Ara gün listesi; liman turu kış tarifesi.
- **05-belge:** randevusuz/acil başvuru kategorileri; mfa.gov.tr yeşil pasaport muafiyet sayfası; DWD Aralık normali; TCMB 19–20.10 kur dosyası; 7 günlük Türk sigortacı primi; Hamburg Glühwein bardak depozitosu; iDATA Antalya güncel saatleri; Vodafone paket fiyatları; kamu hekimi yurt dışı izin prosedürü; gün ışığı için kaynak yok (04 NOAA hesabıyla kapatmış).
- **PLAN:** §9/9 listesi yukarıdakilerin çoğunu kapsıyor; eksikler: AntRay durağı/km, Wochenkarte kuralı, feribot 62 kış tarifesi, MADISON bagaj, Fleetschlösschen/Daniel Wischer adresi, Buddenbrookhaus, Vodafone (§9/8'de kısmen var).
- **Bu denetimde yeni boşluklar:** iDATA 39,92/12 € resmî teyidi; ECB 19.10 bülteni; Lindner Pazar check-out; Dialog yetişkin fiyatı; Kunsthalle 2026 fiyatı; HafenCity 2026 tarihleri; Lübeck 2026 resmî tarihleri; XQ170 kış 2026/27 tarifesi.

**5.2 Kullanıcı kararı gereken açık noktalar — birleşik tek liste (öncelik sırası):**
1. **Vize kapısı (K1):** yeşil pasaport / geçerli çok girişli vize / "Ziyaret" bekleme listesi kaydı ve randevu tarihi → yoksa tarih ertelenir; iade edilemez rezervasyon yapılmaz.
2. **Uçuş saati teyidi (S1)** ve dönüş seçimi: XC151 19:10 (213 USD, ayrı bilet, 01:10 eve) / XQ171 13:35 (247 USD, tek PNR, 19:10 eve).
3. **Bagaj:** 8 kg kabin mi 20 kg mı → tarife (SunValue/Eco) ödeme sayfasında; bütçeye eklenecek.
4. **Otel kademesi + iptal primi:** CAB20 (kapsül/ortak banyo kabul?) / Lindner (+261 USD ücretsiz iptal) / MADISON; vize netleşmeden iptalli oda.
5. **Ulaşım biletleme:** Deutschlandticket 63 € (yabancı kart denemesi, ≤10 Ara iptal, güncel fiyat S8) vs hvv günlük + SH-Ticket 79,10 € (Gün 7'de Tageskarte alınmalı; Einzelkarte ile +4,10 €).
6. **Konser:** 8 Ara Sol Gabetta (ab 29,30) / 9 Ara Bach (ab 34, fiyat çelişkili) / hiçbiri; alınırsa Plaza 5 € gereksiz ama gün batımı slotu kaybolur.
7. **UKE ziyareti:** istenir mi; 11 Ara sabah (Rathaus turu yerine) veya 13 Ara sabah; önceden e-posta.
8. **Gün 6 parade:** 14:00 (öğle yemeğiyle çakışır) yerine 17:00.
9. **Sigorta:** Allianz/Anadolu teklif formundan 2 teklif (30.000/50.000 €), 7–13 Ara tam gün.
10. **Nakit miktarı** (100–150 € önerisi) ve eSIM (Airalo 3 GB) tercihi.
11. **Seyahat öncesi kontrol listesi (Aralık başı):** Rathaus tur günleri (11 Ara); liman turu kış tarifesi; Jungfernstieg/St. Petri/Fleetinsel/HafenCity 2026 ilanları; Fischmarkt saat değişikliği; 13 Ara DB tarife değişikliği (S1/RE8); AntRay en yakın durak; Antalya taksi/tramvay zam sonucu; Lindner Pazar check-out; iDATA güncel ücret.

---

## 6. Uydurma taraması

- **Kaynaksız load-bearing sayı:** bulunmadı. PLAN §5 ve §8'deki tüm fiyat/saat/tarih değerleri alt raporlarda numaralı kaynağa bağlı; kaynaksız olanlar açıkça işaretli ("helal et … kaynak yok", "Glühwein bardak depozitosu bulunamadı", "gün ışığı NOAA hesabı [çıkarım]").
- **"Yaklaşık/genellikle" ile geçiştirilmiş iddialar:** "Hava Aralık ort. ~3 °C, 10–18 yağışlı gün" [doğrulanmalı] etiketli ve iki kaynaklı (climate-data, wetterdienst) — kabul; "EES ~15 dk kuyruk" [doğrulanmalı] — kabul; "Glühwein ~4,50–5 €" [doğrulanmalı] — kabul; "Yemek 45 €/gün" [çıkarım], Numbeo'ya bağlı — kabul; "AntRay ~20 dk'da bir, ~05:50–23:23" [doğrulanmalı], üçüncü taraf — kabul (yedek seçenek, load-bearing değil); "kontuarlar genelde 2–3 sa önce açılır" (03) hamburg-airport.de atıflı — kabul.
- **Etiket şişirmesi:** 9 iddia `[kesin]` etiketiyle yazılmış ama erişilebilir resmî kaynakta birebir bulunamadı (§1 #3, #5, #6, #11, #13, #19, #21, #25, #26). Ortam kısıtı (sayfa açılamadı) göz önünde; hiçbiri uydurma değil, hepsi başka bağımsız kaynakla tutarlı. Etiketler `[doğrulanmalı]`'ya düşürülmeli.
- **Araç çıktısı etiketleri:** uçuş/otel fiyat ve saatleri protokol gereği `[kesin]` (araç çıktısı, 20.10 damgalı) — uygun; ancak XQ170 saatinin mevsimselliği (S1) PLAN'a not düşülmeli.

---

## 7. Düzeltme önerileri (dosyalar değiştirilmedi)

| Dosya | Yer | Öneri |
|---|---|---|
| PLAN.md | Başlık kur satırı | `[kesin]` → `[doğrulanmalı]` (ECB 19.10 sayfası açılamadı; 13.10 değeriyle tutarlı) |
| PLAN.md | §0 ücret cümlesi | "90 € `[kesin]` + 39,92 € (+12 €) `[doğrulanmalı]`"; "15/45 gün" → `[doğrulanmalı]` (AB Vize Kodu md. 23) |
| PLAN.md | §0 yeşil pasaport hücresi | `[doğrulanmalı]` etiketi ekle + "mfa.gov.tr'den teyit" |
| PLAN.md | §3 Lindner satırı | "Pazar 14:00 `[doğrulanmalı]`"; §5 Gün 7 "(Lindner Pazar 14:00)" → "(11:00; Pazar 14:00 doğrulanmadı)" |
| PLAN.md | §5 pazar kuralı satırı | "Rathausmarkt 23 Kas–23 Ara `[kesin]`, her gün 11–21 `[doğrulanmalı]`; HafenCity 16 Kas–30 Ara `[doğrulanmalı]`; Santa Pauli `[kesin]`" |
| PLAN.md | §5 Gün 7 | Transfer satırını tek mantığa indir: "15:30 otel (valiz) → 16:00 S1 → ~16:35 HAM → 17:10'dan önce terminal"; "14:30–15:00 Hbf" ibaresini kaldır |
| PLAN.md | §5 Gün 5/§7 | Dialog im Dunkeln "ab 18,50" → "yetişkin 24,50 € `[doğrulanmalı]` (18,50 çocuk)"; müze kalemi 142,50 → 148,50 €; genel toplam 1.930,81 → 1.937,41 € |
| PLAN.md | §5 Gün 6 | Parade 17:00 seçilsin (öğle çakışması) |
| PLAN.md | §6 "20–27 Eki" satırları | "Vize teyidi (§0) sonrası" koşulu ekle; vize netleşmeden yalnız iptalli otel |
| PLAN.md | §2 / §1 | XQ170 satırına "saat mevsimsel; SunExpress'te teyit (yaz 07:00)" notu |
| PLAN.md | §9/9 | Eksik boşlukları ekle (§5.1 "PLAN" maddesi) |
| 01-ucus.md | "Transfer/otel ajanları için kritik saatler" | "evden 08:30" → "07:00–07:30 (03 ile uyumlu)" |
| 02-otel.md | Noel pazarı satırı | Rathausmarkt tarihi `[doğrulanmalı]` → `[kesin]` |
| 04-gezi-programi.md | §2 SH-Ticket, Gün 4 başlığı | 09:00 kuralı `[doğrulanmalı]` → `[kesin]` (bahn.de) |
| 04-gezi-programi.md | §2 Kunsthalle, Dialog | Fiyat etiketleri `[kesin]` → `[doğrulanmalı]`; Dialog yetişkin 24,50 € |
| 04-gezi-programi.md | Gün 1 tablosu | "14:30 Otel check-in" → "14:15–14:30 otel, valiz emaneti; 15:00 oda" |
| 04-gezi-programi.md | §7 ulaşım | 13 Ara: 3 biniş var (Fischmarkt gidiş-dönüş + HAM); "Einzelkarte ×2" yerine "Tageskarte 8,20" yaz (toplam 79,10 değişmez) |
| 05-belge-pratik.md | §1 tablo | 39,92/12 € ve 15/45 gün ve pasaport kuralı satırları `[doğrulanmalı]`; 39,92 yerine "32,81 € (resmî PDF, tarihsiz) – 39,92 € (bulunamadı)" aralığı |
| hesap/butce-kalemleri.json | kalem 5, 7 | Müze 148,50 (Dialog 24,50); vize kalemi etiketi "[kesin] 90 € / [doğrulanmalı] 39,92 €" |

---

**Etiket sayımı (PLAN.md):** denetim öncesi 38 `[kesin]` / 20 `[doğrulanmalı]` / 35 `[çıkarım]`; §7'deki 5 düşürme uygulanınca 33 / 25 / 35. Tüm dosyalar toplamı (öncesi): 228 `[kesin]` / 125 `[doğrulanmalı]` / 132 `[çıkarım]` / 9 `[varsayım]`.

**Plan güvenilirlik özeti: 33 [kesin] / 25 [doğrulanmalı] / 35 [çıkarım]; 1 kırmızı bayrak.**


---

## 8. Uygulanan düzeltmeler (orkestratör, 2026-10-20, denetim sonrası)
§7'deki önerilerin tamamı uygulandı:
- **PLAN.md:** kur etiketi → `[doğrulanmalı]`; §0 ücret/süre/yeşil pasaport etiketleri düşürüldü; §3/§5 Lindner Pazar 14:00 → `[doğrulanmalı]`, check-out 11:00 esas; §5 pazar tarih/saat etiketleri ayrıştırıldı; Gün 7 transfer tek mantığa indirildi (15:30 otel → 16:00 S1 → ~16:35 HAM → <17:10 terminal); Dialog im Dunkeln yetişkin 24,50 € → müze kalemi 148,50 €, genel toplam **1.937,41 € ≈ 107.764 TL**, senaryo tablosu yeniden hesaplandı (python); Gün 6 parade 17:00; §6 "20–27 Eki" satırları vize teyidine koşullandı; XQ170 saatine mevsimsel not; §9 boşluklar eklendi; başlığa denetim özeti eklendi.
- **01-ucus.md:** evden çıkış 07:00–07:45 (03 ile uyumlu).
- **02-otel.md:** Rathausmarkt 2026 tarihi `[kesin]`, saatler `[doğrulanmalı]`.
- **04-gezi-programi.md:** SH-Ticket 09:00 kuralı `[kesin]`; Kunsthalle/Dialog fiyat etiketleri `[doğrulanmalı]`, Dialog yetişkin 24,50; Gün 1 "14:15–14:30 valiz emaneti, 15:00 oda"; §7'ye düzeltme notu (227,60 €).
- **05-belge-pratik.md:** iDATA bedeli 32,81–39,92 € `[doğrulanmalı]`; 15/45 gün ve pasaport kuralı `[doğrulanmalı]`.
- **hesap/butce-kalemleri.json:** müze 148,50; vize etiketi ayrıştırıldı; tablo yeniden üretildi.
Kırmızı bayrak K1 (vize randevusu varsayımı) **açık kalır**: kullanıcı §0 sorularını cevaplayana kadar iade edilemez rezervasyon yapılmamalı.
