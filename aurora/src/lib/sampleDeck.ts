import type { Deck } from './types'

/** A ready-made deck so the editor and present mode feel alive on first run. */
export const sampleDeck: Deck = {
  id: 'sample',
  name: 'Aurora Tanıtımı',
  slides: [
    {
      id: 's1',
      layout: 'title',
      theme: 'aurora',
      title: 'Aurora ile Sunum Sanatı',
      subtitle: "Prezi'nin akışı, modern web'in zarafetiyle buluşuyor.",
    },
    {
      id: 's2',
      layout: 'statement',
      theme: 'candy',
      title: 'Fikirler, hareketle hayat bulur.',
      subtitle: '— Aurora',
    },
    {
      id: 's3',
      layout: 'bullets',
      theme: 'ocean',
      title: 'Neden Aurora?',
      bullets: [
        'Sinematik zoom geçişleri',
        'Tek tıkla şık temalar',
        'Tarayıcıda anında düzenleme',
        'Tasarım bilgisi gerektirmez',
      ],
    },
    {
      id: 's4',
      layout: 'section',
      theme: 'forest',
      title: 'Nasıl Çalışır?',
      subtitle: 'Üç basit adım',
    },
    {
      id: 's5',
      layout: 'bullets',
      theme: 'sunset',
      title: 'Üç Adımda Sunum',
      bullets: ['Slaytını yaz', 'Temanı seç', 'Oynat ve büyüle'],
    },
    {
      id: 's6',
      layout: 'statement',
      theme: 'night',
      title: 'Hadi ilk sununu yapalım.',
      subtitle: 'Sağ üstten “Oynat”a bas ✨',
    },
  ],
}
