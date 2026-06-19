# sav2q1 — SPSS `.sav` → Q1 gönderimine uygun makale (Türkçe, Word)

SPSS veri dosyasından başlayıp **Q1 dergi gönderimine uygun titizlikte**, **Türkçe**, **Word (.docx)**
bir akademik makale (sağlık/tıp/hemşirelik) üreten; Claude Code **skill + çok-agent** sistemi.
Tasarım hedefi: **sıfır uydurma** (fabrication) — sayılar ve atıflar mekanik kapılarla güvence altında.

> **Dürüst kapsam:** Bu sistem uydurma *sayı* ve uydurma *kaynağı* mekanik olarak engeller ve raporlamayı
> Q1 standardına (etki büyüklüğü+GA, STROBE/CONSORT/PRISMA, ICMJE) uydurur. **Garanti etmez:** Q1 *kabulü*
> (özgünlük/katkı bilime bağlıdır) ve tam anlamsal hatasızlık. Bu yüzden **iki zorunlu insan kapısı** vardır.

## İki taşıyıcı kural (invariant)

1. **Sayılar:** Sayı üreten TEK yer deterministik istatistik motorudur → tek `results_ledger.json`.
   Yazarlar yalnız defterdeki sayıyı, cümlenin `binding`'indeki `result_id`'ye ait olduğu doğrulanarak
   kullanır. `verify-numeric` binding-bazlı denetler (uydurma + "doğru sayı/yanlış bağlam" → FAIL).
2. **Atıflar:** Kaynak ancak gerçek MCP çağrısından gelen PMID/DOI ile `evidence_store.json`'da var olur.
   `verify-citations`: gerçek id + `VERIFIED` + abstract'tan **birebir destek alıntısı** (uydurma alıntı → FAIL).

## Mimari

```
.claude/skills/makale/SKILL.md     # /makale orkestratörü (aşamalar + insan kapıları + kalite kapıları)
.claude/agents/makale-*.md         # tek sorumlu alt-agentlar (analist, literatür, yazar, doğrulayıcı, hakem, derleyici)
sav2q1/engine/                     # deterministik istatistik (LLM YOK): io_sav, profile, decision_tree, analyses/, effects, ledger, numbers, runner
sav2q1/docx/                       # Word derleme: assemble, styles(tr-TR), references_docx (Vancouver/APA-7)
sav2q1/tools/                      # verify_numeric, verify_citations (anti-halüsinasyon kapıları)
sav2q1/examples/                   # brief.example.yaml + demo fikstürleri
sav2q1/input/ , sav2q1/runs/       # .sav + koşu çıktıları (GİT'E GİRMEZ — veri yönetişimi)
```

## Kurulum

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e sav2q1     # veya: pip install -r sav2q1/requirements.lock.txt
.venv/bin/python -m pytest sav2q1/tests -q     # 20 test yeşil olmalı
```

## Hızlı deneme (sentetik veriyle uçtan uca)

```bash
# 1) Sentetik sağlık veri seti üret (gerçek hasta verisi DEĞİL)
.venv/bin/python scripts/make_synthetic_sav.py sav2q1/input/ornek.sav

# 2) Analiz → sayı defteri
.venv/bin/python -m sav2q1.engine.runner run \
  --sav sav2q1/input/ornek.sav \
  --plan sav2q1/examples/demo/analysis_plan.json \
  --rundir sav2q1/runs/deneme

# 3) Anti-halüsinasyon kapıları
.venv/bin/python -m sav2q1.tools.verify_numeric \
  --section sav2q1/examples/demo/sections/results.json \
  --ledger sav2q1/runs/deneme/results_ledger.json

# 4) Word derle  (örnek bölümleri/evidence'ı rundir'e kopyalayıp)
cp -r sav2q1/examples/demo/sections sav2q1/examples/demo/manuscript.json \
      sav2q1/examples/demo/evidence_store.json sav2q1/runs/deneme/
.venv/bin/python -m sav2q1.docx.assemble --rundir sav2q1/runs/deneme
# → sav2q1/runs/deneme/output/article_tr.docx
```

Tam akış için Claude Code içinde `/makale` komutunu çalıştır.

## Girdi: `brief.yaml`

Analiz, `.sav`'ın yanında verilen `brief.yaml`'a dayanır (araştırma soruları + değişken rolleri,
doğrulayıcı hipotezler, türetilmiş değişkenler, desen, eksik-veri/çokluluk politikası, ICMJE alanları).
Şablon: `sav2q1/examples/brief.example.yaml`. Eksikse methodologist kullanıcıya sorar (uydurmaz).

## Yapım durumu

- **M0 (tamam):** Yürüyen iskelet — motor (tanımlayıcı + grup karşılaştırma, etki büyüklüğü+GA, karar ağacı),
  sayı defteri, binding-bazlı `verify-numeric`, birebir-alıntılı `verify-citations` (gerçek PubMed kaynağı),
  Word derleme (IMRaD + Tablo 1 + Vancouver kaynakça + ICMJE), `/makale` skill + temel agent kadrosu, 20 test.
- **Sonraki (M1–M7):** tam test paketi (ki-kare/korelasyon/regresyon/güvenirlik/EFA-CFA/mediation) + golden-value
  sayısal doğruluk testleri; tablo/şekil üretimi; kalan yazar agentları (Giriş/Yöntem/Öz/başlık);
  hakem→düzeltme döngüsü + resumable orkestrasyon; İngilizce çeviri aşaması.
