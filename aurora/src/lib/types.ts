export type Layout = 'title' | 'statement' | 'bullets' | 'section'

export interface Slide {
  id: string
  /** Visual arrangement of the slide content. */
  layout: Layout
  /** Theme id, see lib/themes.ts */
  theme: string
  title: string
  subtitle?: string
  bullets?: string[]
}

export interface Deck {
  id: string
  name: string
  slides: Slide[]
}

export const LAYOUT_LABELS: Record<Layout, string> = {
  title: 'Başlık',
  statement: 'Vurgu',
  bullets: 'Maddeler',
  section: 'Bölüm',
}
