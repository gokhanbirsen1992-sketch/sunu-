# Kullanılabilirlik Backlog — Çocuk GE Algoritma Kütüphanesi

Loop bu listeyi izler: her turda **en üstteki işaretsiz** maddeyi alır, uygular,
`python3 tools/build.py` ile gezinme katmanını yeniden üretir, maddeyi işaretler,
commit + push eder. Tümü bittiğinde loop durur.

## Yapıldı
- [x] Aranabilir giriş sayfası — `docs/index.html` (canlı arama + kategori filtresi)
- [x] Tek dosyalık, hepsi-bir-arada uygulama — `docs/app.html` (kenar çubuğu + inline görüntüleme)
- [x] Tekrar-üretilebilir build aracı — `tools/build.py` + `tools/series_style.css`

## Sıradaki (öncelik sırasıyla)
- [ ] **Hızlı başvuru kutusu:** Her algoritmanın en üstüne, masthead'in hemen altına
      "Hızlı başvuru" özeti (`callout` bileşeni): en kritik 3–5 madde + ilk-basamak
      doz + en önemli kırmızı bayrak. Belge başına küçük, taranabilir bir kutu.
      (Standalone HTML'leri düzenle; sonra `tools/build.py`.)
- [ ] **Çapraz bağlantılar:** İlgili algoritmalar arasında "İlişkili algoritmalar"
      bölümü (ör. üst GİS kanaması ↔ özofagus varisi ↔ portal HT ↔ siroz). app.html
      içinde `#a-<slug>` çapraya, index'te `pediatrik-<slug>-algoritmasi.html`e bağla.
- [ ] **Aciller görünümü:** app.html'e "🚨 Aciller" filtresi — kırmızı bayrak/acil
      içeren algoritmaları öne çıkaran bir mod; her belgedeki kırmızı bayrak
      bölümünü tek ekranda toplayan bir özet.
- [ ] **Yazdırılabilir cep kartı:** Her algoritma için tek-sayfa "cep kartı" baskı
      stili (`@media print` ile 1 sayfa: tanım + karar özeti + dozlar + bayraklar).
- [ ] **Klavye gezinme + son bakılanlar:** app.html'de `/` ile aramaya odak, ok
      tuşlarıyla liste gezme, localStorage ile "son açılanlar".
- [ ] **Künye standardizasyonu:** Her belgeye sürüm/tarih ve kılavuz künyesi (footer)
      ekle; tutarlı hale getir.
- [ ] **Kitaplık PDF'ini yenile:** İçerik değiştiyse `tools/` ile per-doc PDF +
      birleşik kitaplığı yeniden üret (Chromium + pdfrw).

## Not
- Klinik içeriği değiştiren geliştirmelerde dozları ve kırmızı bayrakları koru;
  "uzmana sevk" dili ekleme (hedef kitle uzman).
- Her tur **tek** madde; küçük, gözden geçirilebilir commit.
