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

Başlık listesi (kapsam) **onaylandı**. Şu an **2-3. adımda**: ilk örnek
algoritma (`sa_02 — Uzamış yenidoğan sarılığı`) uçtan uca üretildi ve şablon
olarak gözden geçirme bekliyor.

### Örnek girdiyi görüntüleme

```bash
python build/preview.py sa_02     # dist/sa_02.html üretir
```

Üretilen `dist/sa_02.html` tarayıcıda açılır; Mermaid akış şeması ve DOI
bağlantılı kaynaklar gömülüdür. (Önizleme Mermaid'i CDN'den yükler; nihai
derleme çevrimdışı tek dosya olacaktır.)

## Kapsam (Konsensüs Temelli Taslak)

`data/topics.yaml`, yüklenen referans uygulamadan **bağımsız** olarak, güncel
pediatrik GE konsensüs rehberlerine dayanılarak hazırlanmış bir taslaktır.
Dayanak rehberlerin künyeleri (ESPGHAN, NASPGHAN, ECCO, Rome Foundation, WAO,
FISPGHAN, INSPPIRE, ASGE) PubMed üzerinden doğrulanmış ve dosyadaki
`key_consensus_sources` bölümünde DOI'leriyle listelenmiştir.

Taslak **iki eksenlidir** — toplam **308 algoritma**. Eksen 1, bir çocuk GE
polikliniğine gelebilecek tüm şikayet/bulgu giriş noktalarını kapsamayı hedefler.

**Eksen 1 — Bulgu / Şikayet temelli** ("hasta ... ile geliyor", 205 algoritma)

| Grup | Algoritma |
|---|---|
| 👄 Ağız, Yutma & Özofagus Şikayetleri | 15 |
| 🤮 Bulantı & Kusma | 11 |
| 💢 Karın Ağrısı | 12 |
| 🎈 Şişkinlik, Gaz, Distansiyon & Kitle | 5 |
| 💧 İshal & Malabsorpsiyon Şikayetleri | 11 |
| 🚽 Kabızlık & Defekasyon Şikayetleri | 10 |
| 🩸 GİS Kanama Şikayetleri | 7 |
| 🎯 Anorektal Şikayetler | 7 |
| 🟡 Sarılık & Kolestaz Şikayetleri | 7 |
| 🍽️ Beslenme, İştah & Büyüme Şikayetleri | 12 |
| 🍼 Bebek (0–12 ay) Spesifik Şikayetler | 9 |
| 🌐 Sistemik & Ekstraintestinal Bulgular | 13 |
| 🔌 Beslenme Tüpü & Stoma Sorunları | 6 |
| 🧪 Laboratuvar Bulguları | 36 |
| 🩻 Görüntüleme & Muayene Bulguları | 22 |
| 🔎 Takip, Tarama & Özel Durumlar | 9 |
| 🚨 Acil Prezentasyonlar | 13 |

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
  topics.yaml         # Başlık listesi / kapsam tanımı (onaylandı)
  entries/            # Her algoritmanın klinik içerik + Mermaid + kaynakları
    sa_02.yaml        # ← ilk örnek/şablon girdi
build/
  preview.py          # Girdi YAML -> önizleme HTML (mini pipeline)
dist/
  sa_02.html          # Üretilen önizleme
```

## Durum

- [x] Repo pediatrik GE projesine dönüştürüldü
- [x] Konsensüs temelli başlık taslağı hazırlandı (`data/topics.yaml`)
- [x] Başlık listesi gözden geçirilip onaylandı (308 algoritma)
- [x] İçerik şeması + ilk örnek girdi (`sa_02`) — PubMed'e çözümlenmiş kaynaklarla
- [x] Örnek için içerik → HTML mini derleme akışı (`build/preview.py`)
- [ ] Şablonun onaylanması, kalan girdilerin üretilmesi
- [ ] Tek dosyalık çevrimdışı HTML uygulaması (tam derleme pipeline'ı)
