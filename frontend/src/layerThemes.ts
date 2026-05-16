import type { LayerTheme } from "./types";

export const LAYER_THEMES: Record<string, LayerTheme> = {
  "1": {
    label: "Kozmoloji",
    glyph: "✦",
    accent: "#a78bfa",
    tagline: "13.8 milyar yıl önce",
  },
  "2": {
    label: "Kimya",
    glyph: "⌬",
    accent: "#60a5fa",
    tagline: "460 nm dalga boyu",
  },
  "3": {
    label: "Hücresel",
    glyph: "◉",
    accent: "#34d399",
    tagline: "Hepatositin iki yüzü",
  },
  "4": {
    label: "Evrim",
    glyph: "↯",
    accent: "#22d3ee",
    tagline: "Memeli olmanın bedeli",
  },
  "5": {
    label: "Embriyoloji",
    glyph: "◐",
    accent: "#f472b6",
    tagline: "26. günde başlayan tomurcuk",
  },
  "6": {
    label: "Etimoloji + Tarih",
    glyph: "§",
    accent: "#fbbf24",
    tagline: "61 yıl, beş hekim",
  },
  "7": {
    label: "Anatomi",
    glyph: "△",
    accent: "#f97316",
    tagline: "Lobül ve asinüs",
  },
  "8": {
    label: "Histoloji",
    glyph: "◇",
    accent: "#a3e635",
    tagline: "25 mikronluk dünya",
  },
  "9": {
    label: "Fizyoloji",
    glyph: "≈",
    accent: "#38bdf8",
    tagline: "Enterohepatik döngü",
  },
  "10": {
    label: "Biyokimya",
    glyph: "Φ",
    accent: "#c084fc",
    tagline: "UGT1A1 — tek enzim",
  },
  "11": {
    label: "Patofizyoloji",
    glyph: "✕",
    accent: "#fb7185",
    tagline: "Kapı kapandığında",
  },
  "12.1": {
    label: "Yıldız: Vaka",
    glyph: "★",
    accent: "#facc15",
    tagline: "Bilirubin 28",
  },
  "12.2": {
    label: "Gilbert",
    glyph: "G",
    accent: "#fde68a",
    tagline: "Hafif varyant",
  },
  "12.3": {
    label: "Crigler-Najjar I",
    glyph: "CN1",
    accent: "#f59e0b",
    tagline: "Yıldız'ın koridoru",
  },
  "12.4": {
    label: "Crigler-Najjar II",
    glyph: "CN2",
    accent: "#fb923c",
    tagline: "Arias varyantı",
  },
  "12.5": {
    label: "Dubin-Johnson",
    glyph: "DJ",
    accent: "#84cc16",
    tagline: "Apikal kapı yok",
  },
  "12.6": {
    label: "Rotor",
    glyph: "R",
    accent: "#06b6d4",
    tagline: "İki kapı birden",
  },
  "12.7": {
    label: "Algoritma",
    glyph: "⇉",
    accent: "#94a3b8",
    tagline: "Yatak başı",
  },
  "12.8": {
    label: "Türkiye",
    glyph: "TR",
    accent: "#ef4444",
    tagline: "Konsangüinite haritası",
  },
  "12.9": {
    label: "Araştırma Boşluğu",
    glyph: "?",
    accent: "#e879f9",
    tagline: "Q1 sorusu",
  },
  "13": {
    label: "Kapanış",
    glyph: "◯",
    accent: "#fef3c7",
    tagline: "Yıldız'a geri dönüş",
  },
};

export const layerTheme = (id: string): LayerTheme =>
  LAYER_THEMES[id] ?? {
    label: `Katman ${id}`,
    glyph: id,
    accent: "#e2e8f0",
    tagline: "",
  };
