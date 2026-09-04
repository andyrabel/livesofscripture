// Minimal service worker: exists mainly to satisfy PWA installability
// criteria and give the site a basic offline fallback. Content changes
// often, so this deliberately does NOT cache HTML pages long-term —
// navigations always try the network first.
const CACHE_NAME = "los-shell-v1";
const SHELL_ASSETS = [
  "/",
  "/manifest.json",
  "/css/style.css",
  "/js/app.js",
  "/favicon.svg",
  "/images/icon-192.png",
  "/images/icon-512.png",
];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(SHELL_ASSETS)).catch(() => {})
  );
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key)))
    )
  );
  self.clients.claim();
});

self.addEventListener("fetch", (event) => {
  const { request } = event;
  if (request.method !== "GET") return;

  const url = new URL(request.url);
  if (url.origin !== self.location.origin) return;

  // Navigations (page loads): network-first so visitors always see the
  // latest content when online, falling back to a cached shell offline.
  if (request.mode === "navigate") {
    event.respondWith(
      fetch(request).catch(() => caches.match("/") )
    );
    return;
  }

  // Static shell assets: cache-first, refreshed in the background.
  if (SHELL_ASSETS.some((path) => url.pathname === path)) {
    event.respondWith(
      caches.match(request).then((cached) => {
        const network = fetch(request)
          .then((response) => {
            caches.open(CACHE_NAME).then((cache) => cache.put(request, response.clone()));
            return response;
          })
          .catch(() => cached);
        return cached || network;
      })
    );
  }
});
