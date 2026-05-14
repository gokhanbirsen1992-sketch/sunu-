# Pediatrik GE — Literatür Temelli Algoritmalar

Pediatrik gastroenteroloji için **literatüre dayalı, PubMed'e çözümlenmiş kaynaklarla**
desteklenen klinik karar algoritmaları. Hedef çıktı; çevrimdışı çalışan, tek dosyalık,
mobil uyumlu bir klinik referans uygulamasıdır.

> ⚠️ Eğitim ve karar destek amaçlıdır; yerel rehberlerin ve klinik muhakemenin yerine geçmez.

## Çalışma Akışı

```
1. Başlıklar (kapsam)   →  data/topics.yaml
2. Klinik içerik        →  her başlık için yapılandırılmış metin
3. Algoritma            →  her başlık için Mermaid akış şeması
4. Kaynaklar            →  her kaynak gerçek makaleye çözümlenir (PMID / DOI)
5. Derleme              →  tek dosyalık HTML uygulaması üretilir
```

Şu an **1. adımdayız**: başlık listesi (kapsam) belirleniyor — taslak hâlinde,
gözden geçirme bekliyor.

## Kapsam (Konsensüs Temelli Taslak)

`data/topics.yaml`, yüklenen referans uygulamadan **bağımsız** olarak, güncel
pediatrik GE konsensüs rehberlerine dayanılarak hazırlanmış bir taslaktır.
Dayanak rehberlerin künyeleri (ESPGHAN, NASPGHAN, ECCO, Rome Foundation, WAO,
FISPGHAN, INSPPIRE, ASGE) PubMed üzerinden doğrulanmış ve dosyadaki
`key_consensus_sources` bölümünde DOI'leriyle listelenmiştir.

Taslak **iki eksenlidir** — toplam **184 algoritma**:

**Eksen 1 — Bulgu / Şikayet temelli** ("hasta ... ile geliyor", 81 algoritma)

| Grup | Algoritma |
|---|---|
| 🧪 Laboratuvar Bulguları | 20 |
| 🩻 Görüntüleme & Muayene Bulguları | 13 |
| 🤚 Semptomlar | 38 |
| 🚨 Acil Prezentasyonlar | 10 |

**Eksen 2 — Hastalık / Durum temelli** (yönetim algoritması, 103 algoritma)

| Grup | Algoritma |
|---|---|
| 🫒 Özofagus & Yutma | 8 |
| 🫃 Mide & Duodenum | 7 |
| 🔵 İnflamatuar Barsak Hastalığı (IBD) | 10 |
| 🦠 Enfeksiyöz & İnflamatuar Enterokolit | 7 |
| 🧬 Besin Alerjisi & Eozinofilik GİS | 6 |
| 🌀 Malabsorpsiyon & Çölyak | 8 |
| 〰️ Fonksiyonel GİS Bozuklukları (Rome IV) | 8 |
| 🧩 Konjenital & Cerrahi Alt GİS | 7 |
| 👶 Neonatal Kolestaz & Safra Yolları | 7 |
| 🟫 Karaciğer: Enfeksiyöz & Otoimmün | 7 |
| 🟤 Karaciğer: Metabolik, Vasküler & Diğer | 11 |
| 🟡 Safra Kesesi & Pankreas Hastalıkları | 9 |
| 🥗 Beslenme & Nütrisyonel Destek | 8 |

Başlık listesini düzenleme talimatları `data/topics.yaml` dosyasının başındadır.

## Dizin Yapısı

```
data/
  topics.yaml     # Başlık listesi / kapsam tanımı  ← şu an buradayız
  entries/        # (sonraki adım) her başlık için klinik içerik + algoritma
build/            # (sonraki adım) HTML derleme pipeline'ı
dist/             # (sonraki adım) üretilen tek dosyalık HTML uygulaması
```

## Durum

- [x] Repo pediatrik GE projesine dönüştürüldü
- [x] Konsensüs temelli başlık taslağı hazırlandı (`data/topics.yaml`)
- [ ] Başlık listesi gözden geçirilip onaylandı
- [ ] İçerik şeması ve örnek girdi
- [ ] PubMed kaynak çözümleme pipeline'ı
- [ ] HTML derleme pipeline'ı
