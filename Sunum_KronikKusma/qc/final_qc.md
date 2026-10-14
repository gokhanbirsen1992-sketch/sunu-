# Son kalite denetimi — Kronik Tekrarlayan Kusması Olan Çocuğa Yaklaşım

Tarih: 2026-10-14 · Dosyalar: `output/KronikKusmaYaklasim.pptx`, `output/KronikKusmaYaklasim.pdf`, `_kaynaklar.md`

## Kaynak ve iddia katmanı
| Kontrol | Sonuç | Dosya |
|---|---|---|
| PubMed referans denetimi (V1) | 154 PMID: FABRICATED 0 · MISMATCH 0 · geri çekilmiş 0 · `submission_safe = true` (+3 yeni PMID orkestratör doğrulaması → 157) | `qc/reference_audit.json` |
| İddia sadakati (V2a/b/c, 281 iddia) | UNSUPPORTED 0 · QUOTE_NOT_FOUND 0 · PARTIAL 91 / OVERSTATED 5 → yalnız düzeltilmiş halleri slaytta | `qc/claim_fidelity_V2*.md`, `qc/adjudication.md` |
| Klinik denetim (V3) | 9 KRİTİK, 19 ÖNEMLİ, 10 KÜÇÜK → karara bağlandı | `qc/clinical_review.md`, `qc/adjudication.md` |
| Deterministik sayı/PMID/DOI kontrolü | 303 iddia; bib sorunu 0, çakışma 0; 57 satırda iddiadaki sayı (çoğu n/yıl) alıntı dışında — elle incelendi | `qc/evidence_check.json` |
| Slayttaki her kaynak | 88 kaynak; her biri `library.bib`'de ve en az bir kanıt satırında (build_refs.py zorunlu kılar) | `_kaynaklar.md`, `references/ref_order.json` |
| Deck metni ↔ onaylı içerik | 243 metin parçası; 236 birebir, 7'si bilinçli düzen dönüşümü (kart başlığına dönen "Süt çocuğu:" gibi) | `qc/deck_text.md` |
| Anahtar sayı kartları | Her kart sayısının slayt metninde geçtiği kod içinde denetlenir (yeni iddia üretilemez) | `build_deck.js` keyFigure() |

## Deck katmanı
| Kontrol | Sonuç |
|---|---|
| OOXML doğrulama (pptx skill validate.py) | PASSED |
| Slayt sayısı | 49 (1 kapak, 1 yol haritası, 40 içerik, 1 kapanış mesajı, 5 kaynak, 1 teşekkür); app.xml Slides=49 |
| Konuşmacı notu | Metin içeren not 0. Not: pptxgenjs her slayda boş not sayfası yazar → app.xml Notes=49 (boş) |
| Gövde kelime bütçesi ≤40 | İhlal 0; istisna (tablo/kriter/görsel/kart): slayt 9, 12, 23, 24, 28, 31, 32, 33, 37, 42, 43 ve kaynak slaytları |
| Font | Cambria (başlık) + Calibri (gövde); ikisi de Office ile gelir, LibreOffice'te metrik uyumlu (Caladea/Carlito) |
| AI-tell taraması | 0 (uzun tireler iki nokta/noktalı virgülle değiştirildi) |
| Grafik paleti | dataviz validator: teal 00938A + mercan D9573B → tüm kontroller PASS (CVD ΔE 12,1) |
| Bilinen pptxgenjs hatası | Paragraf içi çoklu `<a:pPr>` → `tools/fix_ppr.py` ile her paragrafta tek pPr |
| Görsel QA | Bağımsız denetçi raporu: `qc/visual_qa.md` |

## Yeniden üretim
```
export NODE_MODULES=<pptxgenjs node_modules> PPTX_SKILL_DIR=<pptx skill dizini>
bash tools/build_all.sh      # kaynak numaraları → slides.json → şekiller → PPTX → pPr düzeltme → doğrulama
bash tools/render.sh <dizin> # PDF + PNG + paftalar
python3 tools/deck_qc.py output/KronikKusmaYaklasim.pptx --exempt 9,12,23,24,28,31,32,33,37,42,43,44,45,46,47,48
```
İçerik değişikliği yalnız `research/slides_content.md` üzerinden yapılır; deck metni oradan otomatik okunur.
