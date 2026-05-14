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
pediatrik GE konsensüs rehberlerine dayanılarak hazırlanmış bir taslaktır:
**11 klinik alan / 68 algoritma**. Dayanak rehberlerin künyeleri (ESPGHAN,
NASPGHAN, ECCO, Rome Foundation, WAO vb.) PubMed üzerinden doğrulanmış ve
dosyadaki `key_consensus_sources` bölümünde DOI'leriyle listelenmiştir.

| Klinik Alan | Algoritma |
|---|---|
| 〰️ Fonksiyonel GİS Bozuklukları (Rome IV) | 7 |
| 🫒 Özofagus & Yutma | 9 |
| 🫃 Mide–Duodenum & Üst GİS Kanama | 6 |
| 💧 Akut & Kronik İshal, Malabsorpsiyon | 6 |
| 🧬 Besin Alerjileri & Eozinofilik Hastalıklar | 4 |
| 🔵 İnflamatuar Barsak Hastalığı (IBD) | 8 |
| 🩸 Alt GİS Kanama & Akut Karın | 6 |
| 👶 Neonatal Kolestaz & Safra Yolları | 5 |
| 🟫 Karaciğer Hastalıkları & Yetmezlik | 8 |
| 🟡 Pankreas Hastalıkları | 3 |
| 🥗 Beslenme & İntestinal Yetmezlik | 6 |

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
