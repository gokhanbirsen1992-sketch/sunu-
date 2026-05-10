---
name: iddaa-kupon
description: Günlük futbol bülteninden (PDF/TXT) sadece Maç Sonucu (1X2) marketinde 3 risk profilli (güvenli/dengeli/riskli) iddaa kuponu önerir. Multi-agent yapıda çalışır — parser, istatistik uzmanı, form analisti, kupon kurucu ve denetçi olmak üzere 5 agent'ı orkestre eder. Kullanıcı "kupon yap", "iddaa kuponu", "bültene bak" dediğinde tetiklenir.
---

# İddaa Kupon Önericisi (Multi-Agent)

> ⚠️ **Uyarı:** Bu skill yatırım/kumar tavsiyesi değildir, eğitim/eğlence amaçlıdır. Kayıp riski kullanıcıya aittir. 18+ ve yasal bahis kullanın.

## Mimari

```
KULLANICI
   │  "kupon yap"
   ▼
SKILL: iddaa-kupon (orkestratör)
   │
   ▼
┌──────────────────┐
│ iddaa-denetci ⭐ │  ← üst ajan, tüm akışı koordine eder
│  (Supervisor)    │
└────────┬─────────┘
         │ 1. çağırır
         ▼
   ┌──────────────┐
   │ iddaa-parser │  bülteni oku, sadece futbol+MS oranları çıkar
   └──────┬───────┘
          │ JSON{maclar:[...]}
          ▼
   ┌──────────────────┐
   │ iddaa-istatistik │  vig-free fair prob + güven skoru
   └──────┬───────────┘
          │ JSON enrichlenmiş
          ▼
   ┌────────────────────┐
   │ iddaa-formanalisti │  takım formu/h2h/sakatlık (web)
   └──────┬─────────────┘  → doğrula/şüpheli/red
          ▼
   ┌────────────────────┐
   │ iddaa-kupon-kurucu │  3 profilde kupon (havuzdan seç)
   └──────┬─────────────┘
          ▼
   denetçi → final çıktı + risk uyarısı → KULLANICI
```

## Kapsam (KISITLAR)

- **Sadece futbol** (basketbol/tenis vs. yok)
- **Sadece MS marketi** (Alt/Üst, KG, İY/MS, Handikap yok)
- **Tek kupon değil — 3 profil** (güvenli/dengeli/riskli)

## Kullanım akışı (denetçi'nin çalıştırma sırası)

Kullanıcı "kupon yap" / "iddaa kuponu" dediğinde, **doğrudan `iddaa-denetci` agent'ını çağır** ve bülten dosya yolunu (PDF veya TXT) ya da yapıştırılan metni geç.

```
Agent(subagent_type="iddaa-denetci",
      prompt="Bülten: <dosya_yolu_veya_metin>. Bugünün tarihi: <YYYY-MM-DD>.
              Akışı orkestre et: parser → istatistik → form → kupon → final.")
```

Denetçi sırayla diğer 4 agent'ı çağırır, her birini doğrular, gerekirse düzeltme talebi gönderir, son kuponu sunar.

## Eğer denetçi kullanılmıyorsa (manuel mod)

Doğrudan zincirle:

1. `iddaa-parser` → bülten parse, JSON
2. `iddaa-istatistik` → fair prob ekle, JSON+
3. `iddaa-formanalisti` → web ile doğrula/eler
4. `iddaa-kupon-kurucu` → 3 profil markdown

Her agent'ın çıktısını bir sonrakine girdi olarak ver.

## Veri kaynakları

### Birincil: PDF/TXT bülten (kullanıcı yapıştırır)
- Nesine, Misli, Bilyoner bülten PDF'leri
- Parser `pdftotext -layout` ile metne çevirir
- Kolon başlıkları: MAÇ SONUCU `1 0 2` → MS_1, MS_X, MS_2

### İkincil: API (opsiyonel)
- The Odds API (`ODDS_API_KEY` `.env`'de) — bülten yoksa veya doğrulama için
- API down ise parser otomatik manuel moda düşer

## Çeşitlendirme kuralları (kupon-kurucu uygular, denetçi denetler)

1. Aynı kuponda **aynı ligten max 2 maç**
2. Aynı kuponda **aynı maç tek seçim** olabilir
3. Aynı saat dilimine 3+ maç yığılmaz (korelasyon riski)
4. "Şüpheli" etiketli maç sadece **Riskli** kuponda
5. Her kuponda **min 1 farklı saat** olsun

## Profil kuralları özet

| Profil | Maç | Tek oran | Toplam | Min güven |
|---|---|---|---|---|
| 🛡️ Güvenli | 2-3 | 1.40-2.00 | 2.5-5 | ≥55 |
| ⚖️ Dengeli | 3-5 | 1.50-2.80 | 6-15 | ≥48 |
| 🎲 Riskli | 5-7 | 1.50-4.50 | 20-80 | ≥42 |

## Önemli

- Hiç bir agent **"garantili", "kesin"** demez — denetçi bunu yakalar
- Final çıktıda **risk uyarısı, bütçe önerisi (yarım Kelly)** olur
- Tek bookmaker oranı → "value/edge" ifadesi kullanılmaz; "fair probability" / "güven skoru" kullanılır
- Kullanıcı API down derse → parser manuel mod (yapıştırılan bülten)

## Hızlı test (skill çalışıyor mu?)

```bash
ls -1 /home/user/sunu-/.claude/agents/ | grep iddaa-
# Bekleniyor: 5 dosya
#   iddaa-denetci.md
#   iddaa-formanalisti.md
#   iddaa-istatistik.md
#   iddaa-kupon-kurucu.md
#   iddaa-parser.md
```
