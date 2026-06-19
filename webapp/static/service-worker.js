// PWA service worker — uygulama kabuğunu önbelleğe alır; API çağrıları daima ağdan.
const CACHE = "makale-v1";
const SHELL = ["/", "/static/manifest.webmanifest", "/static/icon-192.png", "/static/icon-512.png"];

self.addEventListener("install", (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(SHELL)).catch(() => {}));
  self.skipWaiting();
});
self.addEventListener("activate", (e) => {
  e.waitUntil(caches.keys().then((ks) => Promise.all(ks.filter((k) => k !== CACHE).map((k) => caches.delete(k)))));
  self.clients.claim();
});
self.addEventListener("fetch", (e) => {
  const url = new URL(e.request.url);
  if (url.pathname.startsWith("/api/")) return;            // dinamik: ağdan
  e.respondWith(caches.match(e.request).then((r) => r || fetch(e.request)));
});
