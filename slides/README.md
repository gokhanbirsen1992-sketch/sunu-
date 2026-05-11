# Yıldız'ın Sarılığı — Slidev Sunusu

Bir herediter hiperbilirubinemi anlatısı. Uzm. Dr. Gökhan Birşen — Antalya Eğitim ve Araştırma Hastanesi.

## Kurulum

```bash
cd slides
pnpm install   # veya: npm install
```

## Geliştirme

```bash
pnpm dev       # http://localhost:3030 açar
```

## PDF Dışa Aktarma

```bash
pnpm add -D playwright-chromium
pnpm export
```

## Statik Site Üretimi

```bash
pnpm build
```

`dist/` klasörü herhangi bir statik barındırıcıya (Netlify, Vercel, GitHub Pages) yüklenebilir.
