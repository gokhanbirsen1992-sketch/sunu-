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

Kurulum gerektirmez. Tek dosya:

```bash
# 1) Doğrudan aç
sindirim-sistemi-3b/index.html  dosyasını çift tıklayıp tarayıcıda aç

# 2) ya da yerel sunucu ile (önerilir)
cd sindirim-sistemi-3b
python3 -m http.server 8000
# sonra tarayıcıda:  http://localhost:8000
```

> Not: Three.js kütüphanesi CDN'den yüklendiği için **ilk açılışta internet bağlantısı** gerekir.
> Tamamen çevrimdışı çalışması istenirse `three.min.js` ve `OrbitControls.js` dosyaları proje
> klasörüne indirilip `index.html` içindeki `<script src="...">` yolları yerel dosyalara çevrilebilir.

## 🛠️ Teknolojiler

- **Three.js (r128)** — 3B sahne, geometri, ışıklandırma, OrbitControls
- Saf **HTML + CSS + JavaScript** (derleme adımı yok, bağımlılık yönetimi yok)

## 🧩 Mimari (tek dosya)

`index.html` içinde:
- `ORGANS` — organ adları, renkleri, konumları ve çocuk dostu metinleri
- Geometri üreticileri — `buildMouth`, `buildEsophagus`, `buildStomach`, `buildSmall` (serpentin tüp),
  `buildLarge` (çerçeveleyen tüp), `buildLiver`, `buildExit`
- `yolEgrisi` — elmanın izlediği `CatmullRomCurve3` yol; `asamalar` ile anlatım eşlenir
- Etkileşim — raycast ile tıklama, sprite etiketler, vurgulama, quiz ve yolculuk mantığı

## 🚀 Geliştirme Fikirleri (sonraki adımlar)

- 🔊 Sesli anlatım (Web Speech API ile Türkçe seslendirme)
- 🧫 Karaciğer + pankreas + safra kesesinin yardımcı rollerinin animasyonu
- 🩺 Sık çocukluk çağı durumlarının basit, eğitsel görselleştirmesi (ör. reflü, kabızlık)
- 🏅 Rozet/ödül sistemi ve ilerleme kaydı (localStorage)
- 🌍 Çoklu dil desteği (TR/EN)
- ♿ Erişilebilirlik: klavye ile gezinme, ekran okuyucu etiketleri

## ⚠️ Not

Bu uygulama yalnızca **eğitim amaçlıdır**, tıbbi tanı veya tedavi aracı değildir.
