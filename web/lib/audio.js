// Howler-backed ambient audio manager. Each room can register a single
// looping track; the manager crossfades between them based on which room
// is most-in-view, and starts muted until the user opts in.
//
// If a track's source list is empty (the default), nothing loads, nothing
// plays, and the rest of the experience still works.

const FADE_MS = 1400;
const NORMAL_VOL = 0.55;

export class AudioManager {
  constructor() {
    this.enabled = false;
    this.tracks = new Map();           // id -> { sound, volume }
    this.currentId = null;
    this.howlReady = typeof window !== 'undefined' && !!window.Howl;
    if (!this.howlReady) {
      // Howler script may load late (defer). Re-check on first interaction.
      this._waitForHowl();
    }
  }

  _waitForHowl() {
    const check = () => {
      if (window.Howl) { this.howlReady = true; return; }
      setTimeout(check, 120);
    };
    check();
  }

  // sources: array of URLs (mp3 + ogg fallback). If empty, the track is a no-op.
  register(id, sources = [], { volume = NORMAL_VOL } = {}) {
    if (!sources.length) {
      this.tracks.set(id, { sound: null, volume });
      return;
    }
    const create = () => {
      const sound = new window.Howl({
        src: sources,
        loop: true,
        html5: true,
        volume: 0,
        preload: false,
      });
      this.tracks.set(id, { sound, volume });
    };
    if (this.howlReady) create();
    else {
      const wait = setInterval(() => {
        if (window.Howl) { clearInterval(wait); this.howlReady = true; create(); }
      }, 120);
    }
  }

  setEnabled(on) {
    this.enabled = on;
    if (!on) {
      for (const { sound } of this.tracks.values()) {
        if (sound) sound.fade(sound.volume(), 0, 400);
      }
    } else if (this.currentId) {
      this._fadeTo(this.currentId);
    }
  }

  focus(id) {
    if (this.currentId === id) return;
    this.currentId = id;
    if (!this.enabled) return;
    this._fadeTo(id);
  }

  _fadeTo(id) {
    for (const [tid, t] of this.tracks) {
      if (!t.sound) continue;
      if (tid === id) {
        if (!t.sound.playing()) {
          try { t.sound.play(); } catch {}
        }
        t.sound.fade(t.sound.volume(), t.volume, FADE_MS);
      } else if (t.sound.playing()) {
        const from = t.sound.volume();
        t.sound.fade(from, 0, FADE_MS);
        // Stop after fade to release the audio element.
        setTimeout(() => { if (t.sound.volume() < 0.01) t.sound.stop(); }, FADE_MS + 100);
      }
    }
  }
}
