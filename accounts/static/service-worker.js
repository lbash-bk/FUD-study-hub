const CACHE_NAME = "fud-study-hub-v2"; // Change version when updating
const urlsToCache = [
  '/',
  '/static/css/main.css',
  '/static/js/main.js', 
  '/static/icons/icon-72x72.png',
  '/static/icons/icon-192x192.png',
  '/static/icons/icon-512x512.png'
];

self.addEventListener("install", event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      return cache.addAll(urlsToCache);
    })
  );
  // Force the waiting service worker to become active
  self.skipWaiting();
});

self.addEventListener("fetch", event => {
  // Only cache GET requests
  if (event.request.method !== 'GET') return;
  
  event.respondWith(
    caches.match(event.request).then(response => {
      // Return cached version or fetch from network
      return response || fetch(event.request).then(fetchResponse => {
        // Optional: Cache new requests as they come in
        return caches.open(CACHE_NAME).then(cache => {
          cache.put(event.request, fetchResponse.clone());
          return fetchResponse;
        });
      });
    }).catch(() => {
      // Optional: Return offline page for navigation requests
      if (event.request.mode === 'navigate') {
        return caches.match('/offline.html');
      }
    })
  );
});

self.addEventListener("activate", event => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== CACHE_NAME) {
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
  // Take control of all clients immediately
  self.clients.claim();
});