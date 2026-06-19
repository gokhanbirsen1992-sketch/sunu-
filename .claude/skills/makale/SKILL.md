---
name: makale
description: >
  SPSS .sav dosyasından Q1 dergi gönderimine uygun, halüsinasyon-dirençli TÜRKÇE
  akademik makaleyi (Word/.docx) çok-agentlı boru hattıyla üretir. Sağlık/tıp/
  hemşirelik araştırması, SPSS/.sav analizi, "makale yaz", "Q1 makale", istatistik
  + literatür + IMRaD istendiğinde kullan.
argument-hint: "[sav2q1/input/<dosya>.sav]"
---

# /makale — SAV → Q1 makale orkestratörü

Sen bu boru hattının ORKESTRATÖRÜsün. Aşağıdaki aşamaları SIRAYLA sürer, alt-agentları
çağırır, her çıktıyı şemaya göre doğrular ve KALİTE + İNSAN kapılarını uygularsın.

## Taşıyıcı kurallar (asla ihlal etme)
1. **Sayılar:** Makaledeki HER sayı `results_ledger.json`'dan gelir. Sen sayı uydurmaz/yeniden
   biçimlemezsin. `verify-numeric` FAIL ise assembly YAPILMAZ.
2. **Atıflar:** HER kaynak gerçek bir MCP (PubMed/Consensus) çağrısından gelen PMID/DOI taşır ve
   `evidence_store.json`'da `VERIFIED`'dır. `verify-citations` FAIL ise assembly YAPILMAZ.
3. Tüm Python çağrıları repo kökündeki venv ile: `.venv/bin/python`.

## Ön koşul — bootstrap
`.venv` yoksa kur: `python3 -m venv .venv && .venv/bin/python -m pip install -e sav2q1`.
`.venv/bin/python -m pytest sav2q1/tests -q` yeşil olmalı.

## Aşamalar

**0. Run başlat.** `run_id=<UTCdamga>-<slug>`, `RUN=sav2q1/runs/$run_id/`. `.sav`'ı `$RUN/input/`'a,
`brief.yaml`'ı oku. brief eksikse `sav2q1/examples/brief.example.yaml`'ı şablon alıp kullanıcıdan
eksikleri iste (uydurma).

**1. Profil + plan.** `makale-analyst` ile profil çıkar (`engine.runner profile`). `makale-methodologist`
ile `analysis_plan.json` üret (desen→checklist, RQ→rol, türetilmiş değişken, eksik-veri/çokluluk).

**2. ⛔ İNSAN KAPISI 1.** `analysis_plan.json` özetini (seçilen testler + gerekçeleri, türetilmiş
değişkenler, eksik-veri politikası) kullanıcıya sun ve AÇIK onay iste. Onaysız ilerleme.

**3. Analiz.** `makale-analyst` ile `engine.runner run` → `results_ledger.json` + tablolar/şekiller.
Sayı üreten TEK aşama budur.

**4. Literatür (paralel).** `makale-lit-pubmed` (+ Consensus/Trials) ile YALNIZ konu terimleri
göndererek gerçek kanıt topla → `evidence/*.json`. `makale-evidence-curator` ile re-resolve + birebir
destek alıntısı + retraction bayrağı → `evidence_store.json`.

**5. Yazım (paralel dalgalar).** Dalga A (yalnız ledger): `makale-write-methods`, `makale-write-results`.
Dalga B (yalnız evidence): `makale-write-intro`, `makale-write-discussion`. Sonra `makale-write-abstract`,
`makale-write-front`. Tüm bölümler `section_draft` şemasına uygun, her cümle `binding`'li.

**6. Doğrulama kapıları (paralel).** Her bölüm için:
   `.venv/bin/python -m sav2q1.tools.verify_numeric --section <s> --ledger $RUN/results_ledger.json`
   `.venv/bin/python -m sav2q1.tools.verify_citations --section <s> --evidence $RUN/evidence_store.json`
   FAIL varsa → ilgili yazar-agenta bulguları ver, yalnız o bölümü yeniden yazdır, kapıları tekrar koştur.

**7. Hakem döngüsü.** `makale-reviewer` (mümkünse farklı/güçlü model) düşmanca Q1 değerlendirmesi yapar.
`revise` ise yalnız işaret edilen bölümleri yeniden yazdır; numeric/citation kapılarını tekrar koştur.
**En çok 4 tur.** Aşılırsa en iyi taslağı derle + `output/REVIEW_OUTSTANDING.md`.

**8. Derleme.** Kapılar (numeric==PASS && citations==PASS && reviewer==accept) yeşilse `makale-assembler`
→ `.venv/bin/python -m sav2q1.docx.assemble --rundir $RUN` → `output/article_tr.docx`.

**9. ⛔ İNSAN KAPISI 2.** LLM hakemi DANIŞMANDIR. Makaleyi kullanıcıya sun; "final" için kullanıcı
imzası iste. Q1/SCIE için İngilizce gerekiyorsa `makale-translator-en` ile `article_en.docx` üret
(sayı/PMID/DOI birebir korunur, verify tekrar).

## Durum/özet
Her aşamadan sonra `$RUN/run_manifest.json`'da durumu güncelle; kapı durumlarını ve açık bulguları yaz.
Çökme olursa `done` aşamaları (girdi hash'i sabitse) atlayıp ilk `pending`'den devam et.
