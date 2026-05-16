import { Gallery } from './lib/gallery.js';
import { AudioManager } from './lib/audio.js';

const boot = document.getElementById('boot');
const audioToggle = document.getElementById('audio-toggle');
const dotNav = document.getElementById('dot-nav');

const audio = new AudioManager();
const gallery = new Gallery({
  root: document.getElementById('gallery'),
  audio,
});

// Dot navigation — one dot per section.
const dotState = new Map();
for (const section of document.querySelectorAll('.alcove')) {
  const id = section.dataset.room;
  const title = section.dataset.title ?? id;

  const li = document.createElement('li');
  const btn = document.createElement('button');
  btn.type = 'button';
  btn.title = title;
  btn.setAttribute('aria-label', `Go to ${title}`);
  const span = document.createElement('span');
  span.className = 'dot';
  btn.appendChild(span);
  btn.addEventListener('click', () => {
    section.scrollIntoView({ behavior: 'smooth', block: 'start' });
  });
  li.appendChild(btn);
  dotNav.appendChild(li);
  dotState.set(id, span);
}

window.addEventListener('gallery:focus', (e) => {
  for (const [id, span] of dotState) {
    span.classList.toggle('dot--on', id === e.detail.id);
  }
});

// Audio toggle.
audioToggle.addEventListener('click', () => {
  const next = !audio.enabled;
  audio.setEnabled(next);
  audioToggle.setAttribute('aria-pressed', String(next));
  audioToggle.querySelector('.audio-icon').textContent = next ? '♪' : '○';
});

// Keyboard navigation between sections.
const sections = Array.from(document.querySelectorAll('.alcove'));
let currentIndex = 0;
window.addEventListener('gallery:focus', (e) => {
  const idx = sections.findIndex(s => s.dataset.room === e.detail.id);
  if (idx >= 0) currentIndex = idx;
});

window.addEventListener('keydown', (e) => {
  if (e.target.matches('input, textarea, [contenteditable]')) return;
  let next = currentIndex;
  if (e.key === 'ArrowDown' || e.key === 'PageDown' || e.key === ' ') next = Math.min(sections.length - 1, currentIndex + 1);
  else if (e.key === 'ArrowUp' || e.key === 'PageUp') next = Math.max(0, currentIndex - 1);
  else if (e.key === 'Home') next = 0;
  else if (e.key === 'End') next = sections.length - 1;
  else return;
  e.preventDefault();
  sections[next].scrollIntoView({ behavior: 'smooth', block: 'start' });
});

// Boot fade — once the first room has rendered at least one frame and
// fonts have settled, hide the loader.
requestAnimationFrame(() => {
  // Give the first WebGL context a beat to warm up.
  setTimeout(() => boot.classList.add('is-gone'), 500);
});

// Expose for debugging from the console.
window.__maison = { gallery, audio };
