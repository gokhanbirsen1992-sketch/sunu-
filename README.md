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

Şu an **1. adımdayız**: başlık listesi (kapsam) belirleniyor.

## Kapsam (Aday Havuz)

`data/topics.yaml` içinde 6 modül altında **601 aday başlık** (404 hastalık + 197 şikayet)
bulunuyor. Bu liste, yüklenen referans uygulamadan aday havuz olarak türetildi;
içerik sıfırdan üretilecek.

| Modül | Hastalık | Şikayet |
|---|---|---|
| 🟫 Karaciğer | 61 | 39 |
| 🍽️ Üst GİS | 56 | 30 |
| 🩻 Alt GİS | 90 | 47 |
| 🟡 Safra-Pankreas | 66 | 26 |
| 🥗 Beslenme | 76 | 32 |
| 🔵 IBD Pediatri | 55 | 23 |

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
- [x] Aday başlık havuzu çıkarıldı (`data/topics.yaml`)
- [ ] Başlık listesi gözden geçirilip onaylandı
- [ ] İçerik şeması ve örnek girdi
- [ ] PubMed kaynak çözümleme pipeline'ı
- [ ] HTML derleme pipeline'ı
