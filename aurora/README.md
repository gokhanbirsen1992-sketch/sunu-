# Aurora — Modern Sunum Stüdyosu ✨

Prezi tarzı **sinematik geçişlerle**, tarayıcıda şık sunular hazırlamanı sağlayan
modern bir sunum uygulaması. 21st.dev estetiğinde; React + Tailwind + Framer Motion ile yazıldı.

> Bu uygulama, `sunu-` reposundaki kripto botundan **bağımsız** ayrı bir projedir
> ve `aurora/` klasöründe yaşar.

## Özellikler

- 🎬 **Sunum modu** — Prezi tarzı zoom & fade geçişleri, klavye (← → boşluk · Esc) ve tık ile gezinme
- ✏️ **Düzenleyici** — slayt ekle/sil/çoğalt/sırala, canlı önizleme
- 🎨 **6 hazır tema** — tek tıkla gradyan paletleri
- 🧩 **4 düzen** — Başlık · Vurgu · Maddeler · Bölüm
- 💾 **Otomatik kayıt** — sunular tarayıcının `localStorage`'ında saklanır (hesap gerekmez)
- 🌑 **Landing page** — animasyonlu gradyan, cam efektli kartlar

## Hızlı başlangıç

```bash
cd aurora
npm install
npm run dev
```

Tarayıcıda `http://localhost:5173` adresini aç.

## Komutlar

| Komut | Açıklama |
|---|---|
| `npm run dev` | Geliştirme sunucusu (canlı yenileme) |
| `npm run build` | Üretim derlemesi (`dist/`) |
| `npm run preview` | Derlenmiş sürümü önizle |
| `npm run typecheck` | TypeScript tip kontrolü |

## Klavye kısayolları (Sunum modu)

| Tuş | İşlev |
|---|---|
| `→` / `Boşluk` / `PageDown` | Sonraki slayt |
| `←` / `PageUp` | Önceki slayt |
| `Home` / `End` | İlk / son slayt |
| `Esc` | Düzenleyiciye dön |

## Mimari

```
aurora/
├── index.html
├── src/
│   ├── main.tsx            # Giriş (HashRouter)
│   ├── App.tsx             # Rotalar: / · /editor · /present
│   ├── lib/
│   │   ├── types.ts        # Slide / Deck / Layout tipleri
│   │   ├── themes.ts       # Gradyan temalar
│   │   ├── store.ts        # zustand + localStorage durum yönetimi
│   │   └── sampleDeck.ts   # Açılışta gelen örnek sunu
│   ├── components/
│   │   ├── ui/Button.tsx
│   │   └── SlideStage.tsx  # 1280×720 sabit tasarımı her yere ölçekler
│   └── pages/
│       ├── Landing.tsx     # Tanıtım sayfası
│       ├── Editor.tsx      # Sunum düzenleyici
│       └── Present.tsx     # Tam ekran sinematik sunum
└── ...
```

## Teknolojiler

React 18 · TypeScript · Vite · Tailwind CSS · Framer Motion · Zustand · lucide-react

## Yol haritası (fikirler)

- [ ] Görsel/resim ekleme ve konumlandırma
- [ ] PDF / PNG dışa aktarma
- [ ] Birden fazla sunu yönetimi
- [ ] Sürükle-bırak ile slayt sıralama
- [ ] Paylaşılabilir bağlantı / canlı dağıtım

## Lisans

MIT
