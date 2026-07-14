# Kullanılabilirlik Backlog — Çocuk GE Algoritma Kütüphanesi

Loop bu listeyi izler: her turda **en üstteki işaretsiz** maddeyi alır, uygular,
`python3 tools/build.py` ile gezinme katmanını yeniden üretir, maddeyi işaretler,
commit + push eder. Tümü bittiğinde loop durur.

Öncelik iki-uzman değerlendirmesine göre belirlendi (kıdemli yazılım mühendisi +
pediyatrik GE profesörü): etki×efor, klinik güvenlik ve erişilebilirlik ağırlıklı.

## Yapıldı
- [x] Aranabilir giriş sayfası — `docs/index.html`
- [x] Tek dosyalık uygulama — `docs/app.html` (kenar çubuğu + inline görüntüleme)
- [x] Tekrar-üretilebilir build aracı — `tools/build.py` + `tools/series_style.css`
- [x] Klavye gezinme + son bakılanlar (`/`, ok tuşları, localStorage)
- [x] **Klinik eş anlamlı arama:** TR eş anlamlı/kısaltma kümeleri (kanama→hematemez/
      melena/hematokezya, sarılık→ikter/kolestaz, ALT/AST, GÖRH, PUCAI… `tools/build.py`
      `CLUSTERS`) her belgenin arama alanına genişletildi.
- [x] **🚨 Aciller filtresi:** Küratörlü zaman-kritik/cerrahi/YB listesi (`EMERG`,
      17 başlık) nav'da 🚨 rozeti + hem app hem index'te "Aciller" çipiyle süzülür.
- [x] **Elle tema düğmesi:** app'te ◐ ile aydınlık/karanlık geçiş, `data-theme` +
      localStorage ile kalıcı.
- [x] **Erişilebilirlik:** landmark/rol (nav/main/search), `aria-live` sonuç duyurusu,
      açılışta başlığa odak, "içeriğe atla", `aria-current`, focus-visible.
- [x] **Geri tuşu / derin bağlantı:** `history.pushState` + `popstate` ile tarayıcı
      geri tuşu belgeler arası çalışır; `#slug` paylaşılabilir.

## Sıradaki (öncelik sırasıyla)
- [ ] **Hızlı başvuru kutusu:** Her algoritmanın en üstüne "Hızlı başvuru" özeti
      (`callout`): en kritik 3–5 madde + ilk-basamak doz + en önemli kırmızı bayrak.
      NOT: 88 belge — üret→denetle **workflow** ile tek turda; sonra `tools/build.py`.
- [ ] **Klinik hesaplayıcılar paneli:** app'e bağımsız bir "Hesaplayıcılar" görünümü —
      idame sıvı (Holliday-Segar), dehidratasyon % + defisit, düzeltilmiş Na, anyon
      açığı, düzeltilmiş kalsiyum; skorlar PAS/Alvarado, PUCAI. (Yalnızca `tools/build.py`
      JS; her sonuçta "değerleri doğrulayın" uyarısı; ölçü birimleri açık.)
- [ ] **Konu kümeleri / çapraz bağlantı:** İlişkili algoritma kümeleri (IBD; portal
      HT–varis–siroz–GİS kanaması; kolestaz–biliyer atrezi–Alagille/PFIC; pankreas).
      Belge sonuna "İlişkili algoritmalar" bağlantıları (app'te `#a-<slug>`).
- [ ] **Performans (lazy render):** 88 gövdeyi başta DOM'a basmak yerine `<template>`/
      JSON'da tut, seçince render et — mobilde ilk yük ve bellek düşer.
- [ ] **Künye standardizasyonu:** Her belgeye sürüm/tarih + kılavuz künyesi (footer)
      görünür ve tutarlı; app'te belge başında küçük "kaynak/tarih" satırı.
- [ ] **Yazdırılabilir cep kartı:** Her algoritma için tek-sayfa baskı stili
      (`@media print`: tanım + karar özeti + dozlar + bayraklar) + "Yazdır" düğmesi.
- [ ] **PWA / barındırma:** `manifest.webmanifest` + ikon; barındırıldığında "ana
      ekrana ekle". (Service worker `file://`de çalışmaz — hosting notu.)
- [ ] **Kitaplık PDF'ini yenile:** İçerik değiştiyse per-doc PDF + birleşik kitaplığı
      yeniden üret (Chromium + pdfrw).

## Not
- Klinik içeriği değiştiren geliştirmelerde dozları ve kırmızı bayrakları koru;
  "uzmana sevk" dili ekleme (hedef kitle uzman). Hesaplayıcılarda birim ve doğrulama
  uyarısı zorunlu.
- Her tur **tek** madde; küçük, gözden geçirilebilir commit. Değişiklik sonrası
  `node --check` + headless render ile app.html'i doğrula.
