const CACHE = "monalex-v1";
const PRECACHE = ["/", "/search", "/conjugaison"];

self.addEventListener("install", (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(PRECACHE)));
  self.skipWaiting();
});

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches
      .keys()
      .then((keys) =>
        Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k)))
      )
  );
  self.clients.claim();
});

self.addEventListener("fetch", (e) => {
  const { request } = e;
  if (request.method !== "GET") return;

  const url = new URL(request.url);
  // Only cache same-origin requests — skip cross-origin (fonts, analytics, etc.)
  if (url.origin !== self.location.origin) return;
  // Never cache API calls — always hit the network
  if (url.pathname.startsWith("/api/")) return;

  e.respondWith(
    fetch(request).then((res) => {
      // Only cache valid responses
      if (res.ok) {
        const clone = res.clone();
        e.waitUntil(
          caches.open(CACHE).then((c) => c.put(request, clone)).catch(() => {})
        );
      }
      return res;
    }).catch(() =>
      caches.match(request).then((r) => r ?? caches.match("/"))
    )
  );
});
