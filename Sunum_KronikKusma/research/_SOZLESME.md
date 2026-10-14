# Araştırma ajanı sözleşmesi (tüm A1–A6 ajanları için bağlayıcı)

Proje: "Kronik Tekrarlayan Kusması Olan Çocuğa Yaklaşım" — çocuk gastroenteroloji uzmanlarına 40 dk Türkçe kongre sunumu.
Bugünün tarihi: 2026-10-14. Fonksiyonel tanı çerçevesi **Rome V (2026)**; Rome IV dili yalnız "Rome IV→V farkı" bağlamında kullanılabilir.

## Araçlar
Önce `ToolSearch` ile şema yükle:
`select:mcp__PubMed__search_articles,mcp__PubMed__get_article_metadata,mcp__PubMed__get_full_text_article,mcp__PubMed__convert_article_ids,mcp__PubMed__find_related_articles`
ve `select:mcp__Consensus__search,mcp__Scite__search_literature,mcp__Wiley_Scholar_Gateway__search_wiley_fulltext,mcp__Clinical_Trials__search_trials`

- **Birincil:** PubMed `search_articles` → `get_article_metadata` (PMID, DOI, başlık, yazar, yıl, dergi, ÖZET).
- Tam metin: PMC ID varsa `get_full_text_article`. Scite `search_literature` (dois + term) ile tam metin alıntısı ve `editorialNotices` (geri çekilme) kontrolü.
- Consensus `search` (medical_mode=true) yalnız **keşif** için; Consensus'ta bulunan her makale PubMed'de PMID+DOI ile doğrulanmadan kullanılamaz. Consensus'u aynı anda en fazla 1 çağrı yap; rate-limit gelirse PubMed'e geç.
- Ağdan doğrudan erişim (curl ile NCBI/Crossref) YOK — yalnız MCP araçları.

## Anti-halüsinasyon kuralları (ihlal = çıktı reddedilir)
1. Bellekten kaynak, yazar, yıl, sayı, doz YAZMA. Prompt'ta "aday" olarak verilen her kaynak bellekten gelmiştir ve **doğrulanmamıştır**; bulamazsan `[DOĞRULANAMADI]` listesine yaz.
2. Her iddia satırı: PMID **ve** DOI `get_article_metadata` ile bu oturumda doğrulanmış olmalı (DOI yoksa "DOI yok" yaz).
3. Her iddia için **verbatim İngilizce alıntı**: kaynağın PubMed özetinden ya da PMC/Scite tam metninden harfiyen kopya. Alıntının yeri belirtilir: `[abstract]`, `[PMC fulltext: bölüm adı]`, `[scite excerpt]`. Parafraz alıntı olarak yazılmaz.
4. Her sayı (yüzde, n, doz, mg/kg, yaş eşiği, OR, duyarlılık) alıntıda **aynen** geçmeli. Alıntıda olmayan sayı iddiaya giremez.
5. Erişkin verisi → "Not" sütununda **ERİŞKİN** etiketi. Vaka sunumu/küçük seri → kanıt düzeyinde açıkça belirt.
6. Çelişen kanıt ayrı bölümde.
7. Geri çekilmiş / expression of concern olan makale kullanılmaz (Scite editorialNotices).
8. Emin olmadığın şeyi iddia etme. Az ama sağlam > çok ama zayıf.

## Çıktı (iki dosya, başka dosyaya yazma)
### 1) `research/A{n}_{konu}.md`
```
# A{n} — {konu}
## Arama kaydı
| Araç | Sorgu | Hit | Not |
## Kanıt tablosu
| ID | İddia (TR, slayta girecek kısa cümle) | Kaynak (İlkYazar Yıl Dergi) | PMID | DOI | Doğrulama aracı | Verbatim alıntı (EN) [yer] | Kanıt türü (kılavuz/SR/MA/RCT/kohort/seri/derleme/uzman görüşü) | Pediatrik/ERİŞKİN | Önerilen slayt # | Not |
## Çelişen / tartışmalı kanıt
## [DOĞRULANAMADI] — aranan ama bulunamayan / doğrulanamayan
## İskelete öneriler (eksik başlık, gereksiz slayt, sıralama)
```
ID biçimi: `A{n}-01`, `A{n}-02`, …  Hedef: 20–40 sağlam iddia.

### 2) `references/A{n}.bib`
Her kullanılan kaynak için BibTeX; anahtar `IlkYazarSoyadıYıl` (çakışırsa a/b). Zorunlu alanlar: author (ilk 3 + "and others"), title, journal, year, volume, pages (varsa), doi, pmid, pmcid (varsa), `verified = {true}`, `verified_by = {PubMed get_article_metadata 2026-10-14}`.

## Son mesajın (orkestratöre dönüş)
En fazla 15 satır: iddia sayısı, kaynak sayısı, [DOĞRULANAMADI] sayısı, en önemli 3 bulgu, en zayıf halka.
