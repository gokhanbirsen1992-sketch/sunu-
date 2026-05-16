/** Positions on a 100×100 grid. Center (50, 50) reserved for Yıldız. */
export const NODE_POSITIONS: Record<string, { x: number; y: number }> = {
  "1": { x: 50, y: 9 }, // Kozmoloji — kuzey kutbu
  "2": { x: 78, y: 16 }, // Kimya
  "3": { x: 86, y: 36 }, // Hücresel
  "4": { x: 20, y: 18 }, // Evrim
  "5": { x: 12, y: 36 }, // Embriyoloji
  "6": { x: 5, y: 55 }, // Etimoloji + Tarih
  "7": { x: 20, y: 56 }, // Anatomi
  "8": { x: 80, y: 56 }, // Histoloji
  "9": { x: 38, y: 26 }, // Fizyoloji
  "10": { x: 30, y: 38 }, // Biyokimya
  "11": { x: 64, y: 38 }, // Patofizyoloji
  "12.1": { x: 50, y: 66 }, // Yıldız vakası — merkezin hemen altında
  "12.2": { x: 32, y: 78 }, // Gilbert
  "12.3": { x: 44, y: 86 }, // CN1
  "12.4": { x: 60, y: 86 }, // CN2
  "12.5": { x: 72, y: 78 }, // Dubin-Johnson
  "12.6": { x: 84, y: 70 }, // Rotor
  "12.7": { x: 18, y: 70 }, // Algoritma
  "12.8": { x: 10, y: 84 }, // Türkiye
  "12.9": { x: 90, y: 88 }, // Q1 boşluk
  "13": { x: 90, y: 14 }, // Kapanış — kuzeydoğu uzakta
};

/** Ince çizgilerle bağlanacak ilişkili katmanlar (takımyıldız hatları). */
export const CONNECTIONS: Array<[string, string]> = [
  // Bilim zinciri: kozmos → kimya → hücre → ...
  ["1", "2"],
  ["2", "3"],
  ["3", "11"],
  ["1", "4"],
  ["4", "5"],
  ["5", "10"],
  ["10", "11"],
  ["7", "8"],
  ["9", "10"],
  ["3", "8"],
  ["6", "5"],
  // Klinik tabaka
  ["11", "12.1"],
  ["12.1", "12.2"],
  ["12.1", "12.3"],
  ["12.3", "12.4"],
  ["12.4", "12.5"],
  ["12.5", "12.6"],
  ["12.2", "12.7"],
  ["12.7", "12.8"],
  ["12.6", "12.9"],
  // Kapanış
  ["12.1", "13"],
  ["12.9", "13"],
];

/** Anlatı sırası — modal'da prev/next için */
export const NARRATIVE_ORDER = [
  "1",
  "2",
  "3",
  "4",
  "5",
  "6",
  "7",
  "8",
  "9",
  "10",
  "11",
  "12.1",
  "12.2",
  "12.3",
  "12.4",
  "12.5",
  "12.6",
  "12.7",
  "12.8",
  "12.9",
  "13",
];
