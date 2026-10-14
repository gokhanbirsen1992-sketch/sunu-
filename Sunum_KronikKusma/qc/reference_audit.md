# V1 — Referans denetimi (A1–A6.bib)

Tarih: 2026-10-14 · Denetçi: V1 · Kaynak: yalnız bu oturumda PubMed MCP araçlarından alınan kayıtlar. Bib dosyalarına dokunulmadı.

## Özet

| Ölçüt | Değer |
|---|---|
| Bib kaydı | 193 (A1 36, A2 27, A3 42, A4 35, A5 12, A6 41) |
| Benzersiz PMID | 154 |
| VERIFIED | **143** |
| MINOR | **11** |
| MISMATCH | **0** |
| FABRICATED | **0** |
| Geri çekilmiş / kaygı bildirimi | **0** |
| Tekrar sorunu (anahtar çakışması dahil) | **5** |
| `submission_safe` | **true** (MISMATCH = 0, FABRICATED = 0, retracted = 0) |

Bütün PMID'ler PubMed'de bulundu ve bib'deki makaleyle eşleşti. İlk yazar, başlık, cilt ve DOI alanlarında içerik farkı yok. PMCID 49 kayıtta iki tarafta birebir aynı. Kalan 105 kayıtta ne PubMed'de ne bib'de PMCID var.

**Birleştirmeden önce düzeltilmeli (formüle girmez ama kritik):** `Karrento2025` anahtarı iki farklı makaleyi gösteriyor. A1 ve A4'te tanı kılavuzu (PMID 40836301), A6'da tedavi kılavuzu (PMID 40223700). Bib dosyaları tek dosyada birleştirilirse BibTeX ilk kaydı tutar ve öteki dosyadaki `\cite{Karrento2025}` yanlış kılavuza gider. Ayrıntı aşağıdaki "Tekrarlar" bölümünde.

## Yöntem (kısa)

- `get_article_metadata` 8 batch halinde çağrıldı (7×20 + 1×14). Son batch'e 39875217 pozitif kontrol olarak eklendi. 1991–2006 arası 20 PMID için `convert_article_ids` ile PMCID olmadığı ayrıca doğrulandı.
- Karşılaştırmada büyük/küçük harf, noktalama, LaTeX kaçışları ve aksanlar normalize edildi. Sayfa aralığı standart kısaltma açılımıyla karşılaştırıldı (`427-71` = `427--471`, `633-8.e1` = `633--638.e1`). Bu normalizasyondan sonra eşit kalanlar fark sayılmadı.
- **MINOR** yalnız normalizasyondan sonra kalan biçim farkları için verildi: ISO dergi kısaltması, quiz sayfaları, e-yayın ve basılı yıl farkı, DOI alanında serbest metin, kaçışsız `&`.
- Yıl farkı çıkan 2 kayıtta basılı yıl `search_articles` ile `[Date - Publication]` aralığı verilerek ayrıca doğrulandı. Negatif kontrol olarak 2019 sorgusu 0 kayıt döndürdü.

## Sorunlu kayıtlar (MINOR, 11 PMID)

| PMID | Dosya:anahtar | Alan | Bib | PubMed | Öneri |
|---|---|---|---|---|---|
| 8604272 | A2.bib:Pfau1996 | doi | `DOI yok` | DOI yok | Alanı boşalt (A1.bib'deki gibi `doi = {}`). Serbest metin BibTeX çıktısında "doi: DOI yok" ya da kırık bağlantı üretir. |
| 30613204 | A6.bib:Bagherian2019 | doi | `DOI yok` | DOI yok | Aynı: alanı boşalt. |
| 25632624 | A6.bib:Treepongkaruna2014 | doi | `DOI yok` | DOI yok | Aynı: alanı boşalt. |
| 24898244 | A6.bib:Cristofori2014 | journal | `Alimentary pharmacology & therapeutics` | Alimentary pharmacology & therapeutics | `\&` yap. Kaçışsız `&` LaTeX derlemesini bozar. |
| 22634989 | A6.bib:Lee2012 | journal | `European journal of gastroenterology & hepatology` | European journal of gastroenterology & hepatology | `\&` yap (A1/A2'de doğru). |
| 41719916 | A6.bib:Hikita2026 | journal | `Brain & development` | Brain & development | `\&` yap. |
| 23818085 | A1.bib, A3.bib:Parashette2013 | pages | `307--319` | `307-19; quiz 320-1` | Makale sayfaları aynı. PubMed quiz sayfalarını da listeliyor. Düzeltme isteğe bağlı. |
| 29178261 | A4.bib:Rosen2018b | year | 2018 | 2017 (e-yayın 2017-11-27) | Bib basılı yılı kullanıyor (30(3)). Basılı yılın 2018 olduğu `[dp]` aramasıyla doğrulandı. Düzeltme gerekmez; proje genelinde tek bir kural seçilmeli. |
| 28002887 | A4.bib:Rosen2017 | year | 2017 | 2016 (e-yayın 2016-12-21) | Aynı durum. Basılı yılın 2017 olduğu doğrulandı. Düzeltme gerekmez. |
| 29137006 | A1.bib:Morra2017 | journal | `Medicine (Baltimore)` | Medicine (ISO: Medicine (Baltimore)) | NLM ISO biçimi. Düzeltme gerekmez. |
| 33484633 | A3.bib:Husebye2021 | journal | `Lancet` | Lancet (London, England) (ISO: Lancet) | ISO biçimi. Düzeltme gerekmez. |

Not: Öteki bib kayıtları yılı PubMed'in e-yayın yılıyla veriyor (ör. Tarbell2007, Hikita2010, Badihian2017; bunlar `note` alanında basılı yılı belirtiyor). Rosen2017 ve Rosen2018b ise basılı yılı kullanıyor. İkisi de savunulabilir, ama kaynakçada tutarlılık için tek bir kural seçilmeli.

## MISMATCH / FABRICATED

**Yok.** Düzeltilmesi gereken içerik hatası (yazar, yıl, dergi, DOI ya da başlık) bulunmadı. PubMed'de karşılığı olmayan PMID de yok.

## Tekrarlar (5)

| Tür | Ayrıntı | Risk |
|---|---|---|
| Aynı anahtar, farklı PMID | `Karrento2025`: A1, A4 → 40836301 (*…2025 guidelines on the diagnosis of cyclic vomiting…*). A6 → 40223700 (*…2025 guidelines for management of cyclic vomiting…*) | **Yüksek.** Birleştirilmiş bib'de yanlış atıf olur. |
| Aynı PMID, farklı anahtar | 40836301: `Karrento2025` (A1, A4) / `Karrento2025a` (A5) | Kaynakçada çift kayıt. |
| Aynı PMID, farklı anahtar | 40223700: `Karrento2025b` (A5) / `Karrento2025` (A6) | Çift kayıt ve yukarıdaki çakışma. |
| Aynı PMID, farklı anahtar | 29470322: `Rosen2018` (A1, A3) / `Rosen2018a` (A4) | Çift kayıt. |
| Aynı PMID, farklı anahtar | 41713704: `Rosen2026` (A2, A4, A6) / `Rosen2026a` (A5) | Çift kayıt. |

Öneri: tek bir ana bib için anahtarları sabitle, örneğin `Karrento2025dx` = 40836301, `Karrento2025tx` = 40223700, `Rosen2018` = 29470322, `Rosen2026` = 41713704. Ardından A4, A5 ve A6'daki atıfları buna göre güncelle. Aynı DOI'nin farklı PMID'lerle geçtiği bir durum yok. Aynı başlığın farklı PMID'lerle geçtiği bir durum da yok.

Aynı PMID'nin dosyalar arasında içerik çelişkisi yok. Yalnız biçim farkları var: A6 dergi adlarını PubMed'in küçük harfli yazımıyla veriyor; A6 `379--93` ve `1001--6` gibi kısaltılmış sayfa yazıyor; Pfau1996'da DOI A1'de boş, A2'de `DOI yok`; Homan2024'te `{\v z}` ile `{\v{z}}` farkı var. Tam liste: `reference_audit.json` → `audit_meta.cross_file_format_inconsistencies`.

## Geri çekilme, düzeltme ve kaygı kontrolü

- **article_types (154 kayıt):** "Retracted Publication", "Retraction of Publication" ya da "Expression of Concern" taşıyan kayıt yok. Pozitif kontrol 39875217 bu alanda "Retracted Publication" olarak döndü.
- **Konu taraması:** `(retracted publication[pt] OR expression of concern[pt]) AND (vomiting OR emesis OR nausea OR rumination OR gastroparesis)` 283 kayıt döndürdü. Bib PMID'leriyle kesişim **0**. 39875217 bu listede de çıktı.
- **Düzeltme notu taraması:** `published erratum[pt] AND (cyclic vomiting OR rumination OR cannabinoid hyperemesis OR "Rome V" OR …)` 19 not döndürdü, hiçbiri bib makalelerine ait değil. CHS ile ilgili tek not (PMID 38423935) Kum ve ark. Am J Emerg Med 2021 makalesini düzeltiyor. O makale bib'de yok; bib'deki capsaicin kaynağı Dean 2020'dir (PMID 32569429).
- **Şüpheli kayıtlar:** Waisfeld2026'da özet ile başlık arasında hasta sayısı tutarsız (1,375 / 1,373). Pfau1996'nın özetinde bozuk bir cümle var. İkisi için de başlık + (retraction OR erratum OR correction) araması yapıldı, sonuç **0**.
- **Scite:** `search_literature` denendi ve "MCP tools require a paid scite plan or an active free trial" yanıtı geldi. Erişim yok, `editorialNotices` kontrol edilemedi.

## Maaloul 2025 (PMID 39875217) kontrolü

PubMed `article_types` alanı: `["Journal Article", "Retracted Publication"]`. Bu PMID **hiçbir bib kaydında yok.** Geçtiği yerler:

- A2.bib satır 3: yalnız bir `%` yorum satırı (dışlama notu).
- A2_oyku_muayene.md satır 35: arama kaydı.
- A2_oyku_muayene.md satır 71: A2-27 satırının *Not* sütunu. Satırın kaynağı Zheng 2023 (PMID 37237297).
- A2_oyku_muayene.md satır 108: dışlananlar listesi.

Hiçbir iddia satırının kaynak ya da PMID sütununda yer almıyor. **Temiz.**

## Ek gözlemler (karar dışı)

- 5 kaydın PubMed kaydında cilt ve sayfa yok: Benninga2016, Hyams2016, Ananthashayana2026, Rosen2026b, RodriguezManchon2026. Bib'de de bu alanlar boş ve notlarda belirtilmiş. Eksik, ama yanlış değil. Teslimden önce yayımlanmış sayı bilgisi varsa eklenmeli; bu oturumda araçla doğrulanamadı.
- `note` alanları plain/unsrt gibi stillerde kaynakçaya basılır. Bu alanlarda Türkçe iç notlar var ve A1'deki Pfau1996 ile Waisfeld2026 notlarında kaçışsız `#` geçiyor ("Çelişen #3"). Teslim bib'inde `note` alanları kaldırılmalı ya da notu basmayan bir stil kullanılmalı.
- A3.bib'deki Haberle2012 notunda geçen PMID 30982989 de doğrulandı: Häberle 2019, J Inherit Metab Dis 42(6):1192-1230, DOI 10.1002/jimd.12100. Notla uyumlu.
- research/A*.md'de geçip bib'de olmayan PMID'lerin hepsi "kullanılmadı" ya da arama kaydı bağlamında geçiyor. Bib'de olup research'te geçmeyen PMID yok.

Kaynak: PubMed (NCBI) — `get_article_metadata`, `search_articles`, `convert_article_ids`; makale başına DOI'ler `reference_audit.json` içinde.
