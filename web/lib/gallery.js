import { createHero }          from '../rooms/hero.js';
import { createAurore }        from '../rooms/aurore.js';
import { createOnyx }          from '../rooms/onyx.js';
import { createMeridien }      from '../rooms/meridien.js';
import { createConstellation } from '../rooms/constellation.js';
import { createHeritage }      from '../rooms/heritage.js';
import { createOutro }         from '../rooms/outro.js';

const FACTORIES = {
  hero:          createHero,
  aurore:        createAurore,
  onyx:          createOnyx,
  meridien:      createMeridien,
  constellation: createConstellation,
  heritage:      createHeritage,
  outro:         createOutro,
};

// Per-room ambient track URLs. Left empty by default; drop in your own
// loops (mp3 + ogg for fallback) and the manager will pick them up.
export const AMBIENCE = {
  hero:          { sources: [], volume: 0.35 },
  aurore:        { sources: [], volume: 0.45 },
  onyx:          { sources: [], volume: 0.40 },
  meridien:      { sources: [], volume: 0.40 },
  constellation: { sources: [], volume: 0.45 },
  heritage:      { sources: [], volume: 0.40 },
  outro:         { sources: [], volume: 0.30 },
};

export class Gallery {
  constructor({ root, audio }) {
    this.audio = audio;
    this.sections = Array.from(root.querySelectorAll('.alcove'));
    this.rooms = [];

    for (const section of this.sections) {
      const id = section.dataset.room;
      const factory = FACTORIES[id];
      const canvas = section.querySelector('.alcove__canvas');
      if (!factory || !canvas) continue;
      const room = factory(canvas);
      room.id = id;
      room.section = section;
      this.rooms.push(room);
      audio.register(id, AMBIENCE[id]?.sources, { volume: AMBIENCE[id]?.volume });
    }

    this._observe();
  }

  _observe() {
    // A coarse observer to start/stop the render loop. We pad the root
    // margin so a room starts rendering just before it scrolls into view.
    const playObs = new IntersectionObserver((entries) => {
      for (const e of entries) {
        const room = this._roomFromEl(e.target);
        if (!room) continue;
        room.setVisible(e.isIntersecting);
      }
    }, { rootMargin: '20% 0px 20% 0px', threshold: 0 });

    // A fine-grained observer drives intensity and the active audio track.
    const focusObs = new IntersectionObserver((entries) => {
      // pick the entry with the largest intersection ratio.
      let best = null;
      for (const e of entries) {
        const room = this._roomFromEl(e.target);
        if (!room) continue;
        room.setIntensity(e.intersectionRatio);
        room.section.classList.toggle('is-in', e.intersectionRatio > 0.35);
        if (!best || e.intersectionRatio > best.intersectionRatio) best = e;
      }
      if (best && best.intersectionRatio > 0.5) {
        const room = this._roomFromEl(best.target);
        if (room) {
          this.audio.focus(room.id);
          window.dispatchEvent(new CustomEvent('gallery:focus', { detail: { id: room.id } }));
        }
      }
    }, { threshold: [0, 0.25, 0.5, 0.75, 1] });

    for (const room of this.rooms) {
      playObs.observe(room.section);
      focusObs.observe(room.section);
    }
  }

  _roomFromEl(el) {
    return this.rooms.find(r => r.section === el);
  }
}
