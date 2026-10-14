# Hakemlik (orkestratör) — Kapı 2 öncesi

Tarih: 2026-10-14 · Girdi: A1–A6 kanıt dosyaları (281 iddia), A7 hakem ekleri (22 iddia), V1 referans denetimi, V2a/b/c iddia-sadakat denetimleri, V3 klinik denetim, deterministik `tools/check_evidence.py`.

## 1. Sayılarla durum

| Katman | Sonuç |
|---|---|
| Kaynak (V1) | 154 benzersiz PMID PubMed'de: VERIFIED 143 · MINOR 11 (biçim) · **MISMATCH 0 · FABRICATED 0 · geri çekilmiş 0** · `submission_safe = true`. Hakemlikte +3 yeni PMID (41557457, 25957977, 35430344) ve +2 yeniden doğrulanan (27302967, 40544377) orkestratör tarafından PubMed'den kontrol edildi → `library.bib` 157 kayıt |
| İddia sadakati (V2a/b/c, 281 iddia) | SUPPORTED 185 · PARTIAL 91 · OVERSTATED 5 · **UNSUPPORTED 0 · QUOTE_NOT_FOUND 0** |
| Deterministik sayı kontrolü | 303 iddiadan 57'sinde iddiadaki bir sayı alıntıda yok. Tümü elle incelendi: örneklem büyüklüğü (n) ya da yıl gibi alıntı dışında ama aynı özette geçen sayılar. **Gerçek hata 1:** A6-14 (">24 saat" alıntıda yoktu) → A7-14 ile birincil cümle eklendi |
| Klinik denetim (V3) | 9 KRİTİK · 19 ÖNEMLİ · 10 KÜÇÜK → hepsi aşağıda karara bağlandı |
| Slaytta kullanılan | 40 içerik slaytı · 88 kaynak · her madde ≥1 `[@PMID]` + kanıt ID'si (`slides_content.md` "Dayanak") |

Kural: PARTIAL/OVERSTATED bir iddia slayta yalnız denetçinin kaynağa dayalı düzeltilmiş haliyle girdi. Düzeltilmeden kullanılabilecek hali olmayanlar slayta girmedi.

## 2. Kritik kararlar

| # | Konu | Kaynak bayrağı | Karar |
|---|---|---|---|
| K1 | Caimmi 2026 (%16,7 organik) | A2, A3: PubMed'de yok (yalnız MDPI/Consensus) | **SİL.** Plan slayt 3'teki bu sayı kullanılmadı |
| K2 | Waisfeld 2026 SR oranları | A1, A3, V2a, V2b, V3-30: n 1.373/1.375; cerrahi %4,8↔%3,5; migren %12,9↔%17,5; Li 1998'i n=255 aktarıyor; tetikleyici+tanı aynı paydada | **SİL** (ana slaytlardan). Organik oran için Li 1998 kullanıldı |
| K3 | Li 1998 alt oranları (%12 cerrahi / %2 endokrin-metabolik / %7+%5) | V2a, V2b, V3-09: iç tutarsız | **DÜZELT:** yalnız "%88 idiyopatik, kalan ~%12 altta yatan neden" (S5) |
| K4 | Pfau 1996 oranları ve ortalamaları | A1, V2a: özet bozuk, SD imkânsız, eşik-tanım döngüsel | **DÜZELT:** yalnız eşikler (≥4/saat, ≤9/ay) ve n (S4) |
| K5 | Spatuzzo 2025 "kırmızı bayrak OR anlamsız" | V2a, V2b (A3-46 OVERSTATED), V3-13: düzeltilmiş OR, eşdoğrusallık, kusmaya özgü değil, bayraklıda histoloji/US anormalliği anlamlı sık | **DÜZELT:** OR slayttan çıkarıldı; mesaj "organiklerin %38'i bayraksızdı"; popülasyon dipnotu (S11) |
| K6 | A2-17 "Rome V: tetkik yalnız kırmızı bayrakta" | V2a OVERSTATED, V3-12 | **DÜZELT:** SKS ("özellikle bayrak/2 ay") ve KBS ("yalnız alarm") ayrıldı (A7-16, A7-17) |
| K7 | Algoritmada acil dallar yok; safralı kusma yanlış kutuda | V3-01, V3-02 | **DÜZELT:** S20 "Basamak 0" eklendi; safralı kusma → acil grafi + cerrahi |
| K8 | Kritik örnekte ACTH/kortizol ve "dekstroz geciktirilmez" yok | V3-03 | **DÜZELT:** Thornton 2015 (A7-02/03) + Gelfand (A7-15) ile S22 |
| K9 | Rome V SKS ikinci liste başlığı | V2c, V3-24: başlık tam metinde yok | **DÜZELT:** "Eşlik eden özellikler (kutu başlığı doğrulanmadı)" gri kutu; "destekleyici" yazılmadı (S30) |
| K10 | 2008 yaş şeması (≤5/>5) | V3-17: üç kaynakta üç farklı; RCT'de yaş etkisi yok; 2025 özetlerinde yaş yok | **DÜZELT:** "tarihsel" gri kutu (S35); "2025 kaldırdı" denmedi |
| K11 | Erişkin dozları (sumatriptan, lorazepam, baklofen 10 mg ×3, haloperidol mg/kg, D5NS, takviyeler) | V3-20 | **SİL:** hiçbiri slaytta yok |
| K12 | Rome V kriter çevirilerinde "fully" düşmüş | V2c (A5-13/29/33) | **DÜZELT:** "tam olarak açıklanamaz" (S30, S31) |

## 3. Diğer düzeltmeler (ÖNEMLİ/KÜÇÜK)

- Fizyoloji slaytı **silindi** (V3-37; temel bilim/hayvan verisi, uzman dinleyici için gereksiz).
- A2-39 "pozitif tanı tedavidir" (OVERSTATED) → Fitzpatrick 2007 birincil verisi, "ebeveyn algısı" etiketiyle (A7-22, S33).
- A4-28 "her zaman EGD" (OVERSTATED) → "ataklar arası süren yakınmada düşünülür" (S24).
- A6-51 "2 ayda tanıyı sorgula" (OVERSTATED) → Rome V'in betimleyici SKS cümlesi (S39).
- A3-24 2. cümle ("kızda kusma → OTC") kaynaksız → silindi; yalnız lyonizasyon değişkenliği (S17).
- A4-15 Sato → "kortizol örneği anlamlı" çıkarımı → silindi; Sato yalnız muayenede hipertansiyon ipucu (A7-07, S9).
- A2-06 payda: "atakların" → "hastaların ~3/4'ü" (S8).
- A2-26: Goh "%40" → "12/32" (kaynak aritmetiği %37,5).
- A3-29/A4-13: Moses %38 yalnız test edilen alt grup → slaytta %38 kullanılmadı; yalnız görüntüleme bulguları (S23).
- A4-17: Powell %41 duyarlılık değil → kullanılmadı.
- A4-43: 6125 $ = 2015 "fatura" (charge), 3. basamak (S27).
- A6-22/A7-20: topiramat sonlanımları doğru eşleştirildi (tam kurtulma %39 RCT ↔ %81 Türkiye serisi).
- A6-48/Hernandez: yazarların kendi "We recommend" cümleleri NASPGHAN'a mal edilmedi; Hernandez öneri numaraları slayta konmadı.
- Hikita 2026 seçici alıntı → kullanılmadı (V2c, V3-32).
- Nurko %1,1: tablo sayıları ≈%1,4 → slaytta "≈%1" + dipnot (S2).
- Anksiyete %59: Li 2018'e göre okul çağı anksiyete oranı (V3-34) → "%15–59 (ölçüm ve yaşa göre)" (S12).
- Malagelada 2025 etiketi "ERİŞKİN" → "pediatriye özgü değil" (V2a).
- Çölyak: A3 ↔ A4 çelişkisi → "derleme düzeyinde öneri" (V3-11, S15).
- Terminoloji V3-36 tablosuna göre birleştirildi (SKS, KHS, KBS, DGBI, disotonomi, YAOB, süt çocuğu, İSPA).

## 4. Yeni eklenenler (V3 önerisi, orkestratör doğruladı)
Akalazya (Neville 2025) · İSPA (Rosen 2018) · kritik örnek + ACTH/kortizol + ilaç/toksin (Thornton 2015) · adolesan gebelik (Onwuka 2022, DOLAYLI) · Sato hipertansiyonu, TSA titrasyonu/QT, katamenial hormon tedavisi (Li 2018, UZMAN) · TSA dozu, aprepitant–OKS etkileşimi, öneri güçleri (Hernandez 2025, İKİNCİL) · çölyak–DGBI örtüşmesi (Krueger 2025) · erişkin KHS kodu (Sperber 2026, ERİŞKİN). Kanıt satırları: `research/A7_hakem_ekleri.md`.

## 5. Açık maddeler (kapatılamadı — dürüst liste)

| # | Madde | Etki | Varsayılan karar (sen değiştirmedikçe) |
|---|---|---|---|
| O1 | NASPGHAN 2025 tanı (JPGN 81(5)) ve tedavi (JPGN 80(6)) kılavuzlarının **tam metni** görülmedi; bu ortamda PMC/Wiley/Scite erişimi yok | Algoritma kutuları, öneri kesinlikleri, yaş/doz ayrıntısı | Özet + Hernandez 2025 ikincil özeti; slaytlarda "tam metin görülmedi" dipnotu |
| O2 | Rome V pediatrik makalesinin **dergi PDF'i**: SKS ikinci liste başlığı, KBS/EPS "Must include … of" boşluğu, FD'de düşen organizma adı | S30, S31 | Nötr başlık, niceleyici yazılmadı |
| O3 | Batın US: tarama mı, hedefe yönelik mi? (Kovacic 2021 ↔ NASPGHAN 2025) | S21 | Çelişki slaytta açıkça yazıldı; algoritmada "hedefe yönelik / atak sırasında" |
| O4 | Aprepitant pediatrik dozu (>20 kg 125/80/80 mg; erişkin kılavuzunun aktardığı retrospektif seri) | S36 | **Gösterilmedi** |
| O5 | Rizatriptan/aprepitantın Türkiye pediatrik ruhsat durumu | — | Slayta ruhsat bilgisi konmadı |
| O6 | Stres dozu hidrokortizon, taranacak ilaç/toksin listesi, kronik invajinasyon, İİH, hiperkalsemi, nefrolitiyazis için pediatrik kaynak | S18, S20 | "Kaynak doğrulanmadı" dipnotu ya da hiç yazılmadı |
| O7 | Abdominal migren Rome V kriter metni (Di Lorenzo 2026 PMC'de yok) | — | Kriter listesi yok |
| O8 | Scite geri çekilme taraması (ücretli plan) | Tüm kaynaklar | PubMed article_types + V1'in 283 kayıtlık geri çekilme/EoC çapraz taraması ile yapıldı (eşleşme yok) |
| O9 | Konuşmacı adı/kurum/kongre/tarih | S0 | Yer tutucu |

## 6. Plandan sapmalar (bilgi için)
- Ortam bulut Linux konteyneri: PowerPoint COM yerine LibreOffice (PDF/PNG); `search-lit`/`verify-refs`/`present-paper` skill'leri bu ortamda yok → eşdeğerleri `tools/` altında yazıldı (`check_evidence.py`, `merge_bib.py`, `build_refs.py`, `deck_qc.py`).
- Consensus yalnız keşif için; tüm doğrulama PubMed MCP ile.
- Kapı 1: senin gönderdiğin iskelet onaylı taslak sayıldı; revize iskelet (V3 önerisiyle) burada Kapı 2'de sunuluyor.
