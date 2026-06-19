export interface Theme {
  id: string
  name: string
  /** Tailwind gradient classes for the slide background. */
  bg: string
  /** Small swatch gradient (from-/to-) for the picker. */
  chip: string
  /** Accent color used for decorative lines / dots. */
  accent: string
  /** Main text color class. */
  text: string
  /** Muted/secondary text color class. */
  muted: string
}

export const THEMES: Theme[] = [
  {
    id: 'aurora',
    name: 'Aurora',
    bg: 'bg-gradient-to-br from-indigo-600 via-violet-600 to-fuchsia-600',
    chip: 'from-indigo-500 to-fuchsia-500',
    accent: 'bg-fuchsia-300',
    text: 'text-white',
    muted: 'text-white/70',
  },
  {
    id: 'candy',
    name: 'Şeker',
    bg: 'bg-gradient-to-br from-pink-500 via-purple-500 to-indigo-500',
    chip: 'from-pink-500 to-indigo-500',
    accent: 'bg-pink-200',
    text: 'text-white',
    muted: 'text-white/75',
  },
  {
    id: 'ocean',
    name: 'Okyanus',
    bg: 'bg-gradient-to-br from-cyan-500 via-blue-600 to-indigo-700',
    chip: 'from-cyan-400 to-indigo-600',
    accent: 'bg-cyan-200',
    text: 'text-white',
    muted: 'text-white/75',
  },
  {
    id: 'sunset',
    name: 'Günbatımı',
    bg: 'bg-gradient-to-br from-rose-500 via-orange-500 to-amber-400',
    chip: 'from-rose-500 to-amber-400',
    accent: 'bg-amber-100',
    text: 'text-white',
    muted: 'text-white/80',
  },
  {
    id: 'forest',
    name: 'Orman',
    bg: 'bg-gradient-to-br from-emerald-500 via-teal-600 to-green-700',
    chip: 'from-emerald-400 to-teal-600',
    accent: 'bg-emerald-100',
    text: 'text-white',
    muted: 'text-white/75',
  },
  {
    id: 'night',
    name: 'Gece',
    bg: 'bg-gradient-to-br from-zinc-700 via-zinc-900 to-black',
    chip: 'from-zinc-600 to-zinc-900',
    accent: 'bg-violet-400',
    text: 'text-white',
    muted: 'text-white/60',
  },
]

export const getTheme = (id: string): Theme =>
  THEMES.find((t) => t.id === id) ?? THEMES[0]
