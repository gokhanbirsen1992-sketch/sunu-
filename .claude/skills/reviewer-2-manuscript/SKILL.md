---
name: reviewer-2-manuscript
description: Revize edilmiş klinik makaleyi (case report → letter to editor dönüşümü dahil) önceki versiyon ve hakem yorumlarına karşı "Reviewer 2" titizliğiyle denetler; Türkçe, şiddet sıralı rapor üretir. Tetikleyiciler - "reviewer 2", "hakem gibi değerlendir", "revizyonu denetle", "letter to editor değerlendir".
---

# Reviewer-2 manuscript audit

## Akış
1. **Metinleri çıkar** (docx → düz metin):
   `pandoc <dosya>.docx -t plain --wrap=none` (yoksa python-docx).
2. **Kelime/kaynak say** (sandbox'ta hesapla, tahmin etme).
3. **Diff tablosu:** Eski versiyondaki her klinik öğe (tanı testleri, tedaviler + doz/süre, cerrahi + gün,
   laboratuvar değerleri, görüntüleme) → yeni versiyonda: korunmuş / değişmiş / silinmiş.
4. **Hakem yanıt matrisi:** her yorum → Ele alındı / Kısmen / Ele alınmadı / Silinerek kaçınıldı.
5. **Kaynak doğrulama:** `mcp__PubMed__lookup_article_by_citation` → `get_article_metadata`;
   künye + iddia-destek uyumu + Vancouver sıra kontrolü.
6. **Alan-özel kontroller** (pediatrik pankreatit için):
   - CFTR: poliT/TG tekrar bölgesi artefaktı, de novo iddiası için ortogonal doğrulama, ACMG kriter yanlış kullanımı,
     trans varyant/CNV (MLPA) dışlanması, 5T alelinin popülasyon sıklığı (kaynaktan al).
   - Ensefalopati: şok/SIRS/sepsis/metabolik/Wernicke/ilaç ayrımı, zaman çizelgesi, organ disfonksiyon skorları.
   - Splanknik ven trombozu: spontan rekanalizasyon olasılığı, AKI'de enoksaparin dozu/anti-Xa, perioperatif yönetim.
   - Otoimmün pankreatit: IgG4 normalliği tip 2 AIP'yi dışlamaz.
7. **Raporu yaz:** `.claude/agents/reviewer-2.md` içindeki şablon. Çıktıyı çalışma dizinine `.md` olarak kaydet.

## İlkeler
- Silinen uygulanmış tedavi = en yüksek şiddet bulgusu.
- Eski kanıtsız iddianın yerine konan yeni kanıtsız iddiayı yakala.
- Güven etiketleri: [kesin] / [doğrulanmalı] / [çıkarım].
- Paralel iş gerekiyorsa: kaynak doğrulamayı bir alt-ajana, diff + yanıt matrisini ana akışa ver.
