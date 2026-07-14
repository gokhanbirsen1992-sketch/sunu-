# Kullanılabilirlik Backlog — Çocuk GE Algoritma Kütüphanesi

Loop bu listeyi izler: her turda **en üstteki işaretsiz** maddeyi alır, uygular,
`python3 tools/build.py` ile gezinme katmanını yeniden üretir, maddeyi işaretler,
commit + push eder. Tümü bittiğinde loop durur.

## Yapıldı
- [x] Aranabilir giriş sayfası — `docs/index.html` (canlı arama + kategori filtresi)
- [x] Tek dosyalık, hepsi-bir-arada uygulama — `docs/app.html` (kenar çubuğu + inline görüntüleme)
- [x] Tekrar-üretilebilir build aracı — `tools/build.py` + `tools/series_style.css`
- [x] **Klavye gezinme + son bakılanlar:** app.html'de `/` ile aramaya odak, ok
      tuşlarıyla liste gezme + Enter ile açma, localStorage ile "son bakılanlar"
      kısayol satırı.

## Sıradaki (öncelik sırasıyla)
- [ ] **Aciller görünümü:** app.html'e "🚨 Aciller" kısayolu — her belgenin
      kırmızı-bayrak (`alarm-grid`) bölümünü tek ekranda toplayan bir özet görünüm.
      (`tools/build.py`: her belgeden alarm-item'ları çıkar, sahte bir "aciller"
      sayfası oluştur.)
- [ ] **Çapraz bağlantılar:** İlgili algoritmalar arasında "İlişkili algoritmalar"
      bölümü (ör. üst GİS kanaması ↔ özofagus varisi ↔ portal HT ↔ siroz). app.html
      içinde `#a-<slug>` çapraya, index'te `pediatrik-<slug>-algoritmasi.html`e bağla.
- [ ] **Hızlı başvuru kutusu:** Her algoritmanın en üstüne, masthead'in hemen altına
      "Hızlı başvuru" özeti (`callout` bileşeni): en kritik 3–5 madde + ilk-basamak
      doz + en önemli kırmızı bayrak. NOT: 88 belge — bir üret→denetle **workflow**
      ile yap, tek turda. Sonra `tools/build.py`.
- [ ] **Yazdırılabilir cep kartı:** Her algoritma için tek-sayfa "cep kartı" baskı
      stili (`@media print` ile 1 sayfa: tanım + karar özeti + dozlar + bayraklar).
- [ ] **Künye standardizasyonu:** Her belgeye sürüm/tarih ve kılavuz künyesi (footer)
      ekle; tutarlı hale getir.
- [ ] **Kitaplık PDF'ini yenile:** İçerik değiştiyse `tools/` ile per-doc PDF +
      birleşik kitaplığı yeniden üret (Chromium + pdfrw).

## Not
- Klinik içeriği değiştiren geliştirmelerde dozları ve kırmızı bayrakları koru;
  "uzmana sevk" dili ekleme (hedef kitle uzman).
- Her tur **tek** madde; küçük, gözden geçirilebilir commit.
