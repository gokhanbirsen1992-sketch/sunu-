# 🚀 Sindirim Sistemi Macerası — 3B İnteraktif Keşif

Çocuklara yönelik, tarayıcıda çalışan **3 boyutlu interaktif sindirim sistemi** eğitim uygulaması.
Bir elmanın **ağızdan başlayıp ince ve kalın bağırsaklardan geçerek çıkışa** kadar yaptığı yolculuğu
keşfettiren, oyunlaştırılmış (edutainment) bir öğrenme deneyimi.

> Çocuk gastroenteroloji alanına yönelik "yazılım / yapay zeka" proje fikirlerinden biri olarak,
> **klinik dışı / eğitim odaklı** açıyla geliştirilmiş çalışan bir prototip.

## ✨ Özellikler

- 🧬 **3B organ modeli** — Ağız, yemek borusu, mide, ince bağırsak, kalın bağırsak, karaciğer (bonus) ve çıkış.
- 🖱️ **Tıkla & öğren** — Her organa tıklayınca çocuk dostu açıklama + "Bunu biliyor muydun?" eğlenceli bilgi.
- 🍎 **Yolculuk modu** — Bir elma tüm sindirim yolunu kat eder; her aşamada ne olduğu anlatılır.
- 🧠 **Mini quiz** — 5 soruluk, anında geri bildirimli bilgi yarışması ve puanlama.
- 🔄 **Serbest kamera** — Sürükleyerek döndür, tekerlekle yakınlaş; otomatik döndürme seçeneği.
- 📱 **Duyarlı (responsive)** arayüz, tamamen **Türkçe**.

## ▶️ Nasıl Çalıştırılır?

**Kurulum yok, internet yok, bağımlılık yok.** Tek dosya:

```text
sindirim-sistemi-3b/index.html  dosyasını çift tıklayıp tarayıcıda aç — bu kadar.
```

İstersen yerel sunucuyla da açabilirsin:

```bash
cd sindirim-sistemi-3b
python3 -m http.server 8000
# sonra tarayıcıda:  http://localhost:8000
```

> ✅ Dosya **tamamen bağımsızdır**: hiçbir dış kütüphane veya CDN kullanmaz,
> bu yüzden çevrimdışı ortamda ve her tarayıcıda doğrudan açılır.

## 🛠️ Teknolojiler

- Saf **HTML + CSS + JavaScript** — derleme adımı, paket veya bağımlılık yok
- **Kendi mini 3B motoru** (saf `<canvas>` 2D üzerinde): 3B döndürme, perspektif
  projeksiyon ve derinlik (painter) sıralaması elle yazıldı — harici 3B kütüphanesi yok

## 🧩 Mimari (tek dosya)

`index.html` içinde:
- `ORGANS` — organ adları, renkleri, konumları ve çocuk dostu metinleri
- 3B çekirdek — `rot()` (döndürme), `proj()` (perspektif), `smooth()` (Catmull-Rom eğrisi)
- Geometri — `INCE` (serpentin ince bağırsak), `KALIN` (çerçeveleyen kalın bağırsak),
  `GEO` (tüm çizilebilir organlar: tüpler + küreler + yüz)
- `YOL` — elmanın izlediği yol; `ASAMA` ile aşama aşama anlatım eşlenir
- Etkileşim — `pick()` ile tıklama isabeti, fare/dokunma ile döndürme, quiz ve yolculuk mantığı

## 🚀 Geliştirme Fikirleri (sonraki adımlar)

- 🔊 Sesli anlatım (Web Speech API ile Türkçe seslendirme)
- 🧫 Karaciğer + pankreas + safra kesesinin yardımcı rollerinin animasyonu
- 🩺 Sık çocukluk çağı durumlarının basit, eğitsel görselleştirmesi (ör. reflü, kabızlık)
- 🏅 Rozet/ödül sistemi ve ilerleme kaydı (localStorage)
- 🌍 Çoklu dil desteği (TR/EN)
- ♿ Erişilebilirlik: klavye ile gezinme, ekran okuyucu etiketleri

## ⚠️ Not

Bu uygulama yalnızca **eğitim amaçlıdır**, tıbbi tanı veya tedavi aracı değildir.
