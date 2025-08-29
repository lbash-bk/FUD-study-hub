const CACHE_NAME = "fud-study-hub-v3"; // Changed version to v3
const urlsToCache = [
  '/',
  '/static/css/main.css',
  '/static/js/main.js', 
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
        // Cache new requests as they come in (dynamic caching)
        return caches.open(CACHE_NAME).then(cache => {
          // Only cache successful responses and same-origin requests
          if (fetchResponse.status === 200 && event.request.url.startsWith('https://fud-study-hub.onrender.com')) {
            cache.put(event.request, fetchResponse.clone());
          }
          return fetchResponse;
        });
      });
    }).catch(() => {
      // Return a fallback for navigation requests when offline
      if (event.request.mode === 'navigate') {
        return caches.match('/')
          .then(response => response || Response.redirect('/offline.html'));
      }
      return Response.error();
    })
  );
});

self.addEventListener("activate", event => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== CACHE_NAME) {
            console.log('Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
  // Take control of all clients immediately
  self.clients.claim();
});