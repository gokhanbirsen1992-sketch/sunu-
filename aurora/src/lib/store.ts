import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { Deck, Slide, Layout } from './types'
import { sampleDeck } from './sampleDeck'

const uid = () => Math.random().toString(36).slice(2, 9)

function makeSlide(partial?: Partial<Slide>): Slide {
  return {
    id: uid(),
    layout: 'title',
    theme: 'aurora',
    title: 'Yeni Slayt',
    subtitle: '',
    bullets: ['İlk madde', 'İkinci madde'],
    ...partial,
  }
}

interface DeckState {
  deck: Deck
  currentId: string

  setDeckName: (name: string) => void
  select: (id: string) => void
  addSlide: () => void
  duplicateSlide: (id: string) => void
  deleteSlide: (id: string) => void
  updateSlide: (id: string, patch: Partial<Slide>) => void
  move: (id: string, dir: -1 | 1) => void
  resetSample: () => void
}

export const useDeck = create<DeckState>()(
  persist(
    (set, get) => ({
      deck: sampleDeck,
      currentId: sampleDeck.slides[0].id,

      setDeckName: (name) =>
        set((s) => ({ deck: { ...s.deck, name } })),

      select: (id) => set({ currentId: id }),

      addSlide: () =>
        set((s) => {
          const current = s.deck.slides.find((sl) => sl.id === s.currentId)
          const slide = makeSlide({
            theme: current?.theme ?? 'aurora',
            layout: 'bullets',
            title: 'Yeni Slayt',
            subtitle: '',
          })
          const idx = s.deck.slides.findIndex((sl) => sl.id === s.currentId)
          const slides = [...s.deck.slides]
          slides.splice(idx + 1, 0, slide)
          return { deck: { ...s.deck, slides }, currentId: slide.id }
        }),

      duplicateSlide: (id) =>
        set((s) => {
          const idx = s.deck.slides.findIndex((sl) => sl.id === id)
          if (idx === -1) return s
          const copy: Slide = { ...s.deck.slides[idx], id: uid() }
          const slides = [...s.deck.slides]
          slides.splice(idx + 1, 0, copy)
          return { deck: { ...s.deck, slides }, currentId: copy.id }
        }),

      deleteSlide: (id) =>
        set((s) => {
          if (s.deck.slides.length <= 1) return s // keep at least one
          const idx = s.deck.slides.findIndex((sl) => sl.id === id)
          const slides = s.deck.slides.filter((sl) => sl.id !== id)
          const nextCurrent =
            s.currentId === id
              ? slides[Math.max(0, idx - 1)].id
              : s.currentId
          return { deck: { ...s.deck, slides }, currentId: nextCurrent }
        }),

      updateSlide: (id, patch) =>
        set((s) => ({
          deck: {
            ...s.deck,
            slides: s.deck.slides.map((sl) =>
              sl.id === id ? { ...sl, ...patch } : sl,
            ),
          },
        })),

      move: (id, dir) =>
        set((s) => {
          const idx = s.deck.slides.findIndex((sl) => sl.id === id)
          const target = idx + dir
          if (idx === -1 || target < 0 || target >= s.deck.slides.length)
            return s
          const slides = [...s.deck.slides]
          const [item] = slides.splice(idx, 1)
          slides.splice(target, 0, item)
          return { deck: { ...s.deck, slides } }
        }),

      resetSample: () =>
        set({ deck: sampleDeck, currentId: sampleDeck.slides[0].id }),
    }),
    {
      name: 'aurora-deck-v1',
      partialize: (s) => ({ deck: s.deck, currentId: s.currentId }),
    },
  ),
)

export { makeSlide }
export type { Layout }
