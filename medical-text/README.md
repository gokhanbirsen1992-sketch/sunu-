# Yıldız'ın Sarılığı — Sunay Akın Tarzı Yeniden Yazım Sistemi

Bu klasör, 13 katmanlı bir medikal vaka sunumunu (`Yildizin_Sariligi_REVIZE.docx`) Sunay Akın'ın hikâye anlatım tarzında yeniden yazmak için 7 Claude Code subagent'ından oluşan bir çoklu-agent sistemini barındırır.

**Hedef:** Anlatım akıcı, konular bağlı, ilgi çekici hâle gelsin. **Tıbbi sayılar, atıflar ve mekanizmalar değişmesin.**

## Klasör yapısı

```
medical-text/
├── README.md                 ← bu dosya
├── source/
│   ├── Yildizin_Sariligi_REVIZE.docx  ← orijinal
│   └── Yildizin_Sariligi_REVIZE.md    ← agent'ların okuduğu düz metin
├── critiques/                ← her agent'ın eleştiri çıktısı buraya
│   ├── 01-hikaye-anlaticisi.md
│   ├── 02-tarih-etimoloji.md
│   ├── 03-gecis-akis.md
│   ├── 04-siirsel-ritim.md
│   ├── 05-hitap-diyalog.md
│   └── 06-bilimsel-sadakat.md
└── output/
    └── Yildizin_Sariligi_SUNAY_AKIN.md  ← editör agent'ın nihai metni
```

## 7 agent

Tanımları `../.claude/agents/` altında. Her agent kendi bakış açısından metni inceler.

| # | Agent | Görev | Çıktı |
|---|---|---|---|
| 1 | `hikaye-anlaticisi` | Sunay Akın'ın anlatı sesi; açılış kancaları, anlatı yayı | `01-...md` |
| 2 | `tarih-etimoloji-avcisi` | 1054 Yengeç, Hoyle'un tahtası, "ikteros" sarı kuşu vb. cevherleri sahneye taşır | `02-...md` |
| 3 | `gecis-akis-uzmani` | "Sıradaki katmanda" mekanik geçişlerini tematik köprülere çevirir | `03-...md` |
| 4 | `siirsel-ritim-imge` | Üçleme, anafor, somut imge — az ve etkili yamalar | `04-...md` |
| 5 | `hitap-diyalog-uzmani` | "Şimdi düşünün…" türü sahne hitapları, retorik sorular | `05-...md` |
| 6 | `bilimsel-sadakat-bekcisi` | Yazı yazmaz; sayı/atıf/mekanizma kayması olmadığını denetler | `06-...md` |
| 7 | `editor-butunlestirici` | 6 dosyayı okur, tek nihai metni yazar | `output/...md` |

## Çalıştırma

Claude Code içinden subagent'ları sırayla çağır. Adım 2 paralel çalıştırılabilir.

### 1. Eleştiri turu (perspektif agent'ları)

```
> Use the hikaye-anlaticisi agent to critique medical-text/source/Yildizin_Sariligi_REVIZE.md
> Use the tarih-etimoloji-avcisi agent to critique medical-text/source/Yildizin_Sariligi_REVIZE.md
> Use the gecis-akis-uzmani agent to critique medical-text/source/Yildizin_Sariligi_REVIZE.md
> Use the siirsel-ritim-imge agent to critique medical-text/source/Yildizin_Sariligi_REVIZE.md
> Use the hitap-diyalog-uzmani agent to critique medical-text/source/Yildizin_Sariligi_REVIZE.md
```

Her agent `critiques/` altına kendi numaralı dosyasını yazar.

### 2. Bekçi turu (sadakat denetimi)

```
> Use the bilimsel-sadakat-bekcisi agent to audit the 5 critique files in medical-text/critiques/
```

`critiques/06-bilimsel-sadakat.md` üretir — her perspektif eleştirisinin tıbbi sapma yapıp yapmadığı raporu.

### 3. Yazım turu (editör)

```
> Use the editor-butunlestirici agent to produce the final Sunay Akın style text from all critique files
```

`output/Yildizin_Sariligi_SUNAY_AKIN.md` üretilir.

### 4. Son denetim (opsiyonel ama önerilen)

```
> Use the bilimsel-sadakat-bekcisi agent again, this time to audit medical-text/output/Yildizin_Sariligi_SUNAY_AKIN.md against the source
```

Bekçi nihai metinde tüm kritik verilerin korunduğunu teyit eder.

## Kabul kriterleri

Nihai metin (`output/Yildizin_Sariligi_SUNAY_AKIN.md`):

- [ ] 13 katman + Vaka Tanıtımı + Kapanış + Kaynaklar yapısı korunmuş
- [ ] "Sıradaki katmanda" / "Sıradaki katman" ifadeleri sıfırdan en fazla 1-2 kez geçiyor
- [ ] Tüm kritik sayılar mevcut: TBR 28, B/A 8,2, D/T %5,7, 460 nm, 13.8 milyar, 1054, 96. saat, vb.
- [ ] Tüm kaynak atıfları (~30 referans) Kaynaklar listesinde aynen
- [ ] Patofizyoloji 5-sendrom tablosu birebir
- [ ] Klinik Karar üriner CP tablosu birebir
- [ ] Karakter sayısı orijinalin ±%10'u içinde (~40-48 bin)
- [ ] Açılış paragrafı laboratuvar değerleri yerine bir sahneyle başlıyor (sayılar paragrafın devamında)

## Notlar

- Repo'nun ana kodu (kripto sinyal botu, `src/`) bu sistemden bağımsız ve etkilenmez.
- Çıktı `.md` formatında. `.docx` istenirse pandoc ile dönüştürülebilir:
  ```
  pandoc output/Yildizin_Sariligi_SUNAY_AKIN.md -o output/Yildizin_Sariligi_SUNAY_AKIN.docx
  ```
- Eleştiri dosyaları silinebilir; nihai çıktı için kaynak değildirler. Ama denetim izini görmek için tutmak önerilir.
