// Service Worker for {{ pwa_data.app_name }}
// Bump the version to drop every visitor's old cache on their next visit
const CACHE_NAME = 'portfolio-v2';
const OFFLINE_URL = '/static/offline.html';

// Files to cache for offline functionality. Pages are never precached:
// they are always fetched fresh so content, theme and CSRF tokens stay current.
const FILES_TO_CACHE = [
  '/static/css/style.css',
  '/static/js/main.js',
  '/static/icons/icon-192x192.png',
  '/static/icons/icon-512x512.png',
  OFFLINE_URL
];

// Install event - cache resources
self.addEventListener('install', (event) => {
  console.log('[SW] Install');
  
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('[SW] Pre-caching offline page');
        return cache.addAll(FILES_TO_CACHE);
      })
      .then(() => {
        self.skipWaiting();
      })
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  console.log('[SW] Activate');
  
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((thisCacheName) => {
          if (thisCacheName !== CACHE_NAME) {
            console.log('[SW] Removing Cached Files from Cache - ', thisCacheName);
            return caches.delete(thisCacheName);
          }
        })
      );
    }).then(() => {
      self.clients.claim();
    })
  );
});

// Fetch event
self.addEventListener('fetch', (event) => {
  const request = event.request;

  // Only handle same-origin GETs; admin and downloads always go to the network
  if (request.method !== 'GET') return;
  const url = new URL(request.url);
  if (url.origin !== self.location.origin) return;
  if (url.pathname.startsWith('/admin/') || url.pathname.startsWith('/download/')) return;

  // Pages: network first, offline page only when the network is unavailable
  if (request.mode === 'navigate') {
    event.respondWith(
      fetch(request).catch(() => caches.match(OFFLINE_URL))
    );
    return;
  }

  // Static and media assets: serve from cache, refresh the cache in the background
  if (url.pathname.startsWith('/static/') || url.pathname.startsWith('/media/')) {
    event.respondWith(
      caches.open(CACHE_NAME).then((cache) =>
        cache.match(request).then((cached) => {
          const network = fetch(request).then((response) => {
            if (response && response.status === 200 && response.type === 'basic') {
              cache.put(request, response.clone());
            }
            return response;
          }).catch(() => cached);
          return cached || network;
        })
      )
    );
  }
});

// Background sync for form submissions
self.addEventListener('sync', (event) => {
  console.log('[SW] Background Sync', event.tag);
  
  if (event.tag === 'background-sync-contact') {
    event.waitUntil(doBackgroundSync());
  }
});

function doBackgroundSync() {
  // Handle background sync for contact form or other offline submissions
  return new Promise((resolve) => {
    // Implementation for background sync
    console.log('[SW] Performing background sync...');
    resolve();
  });
}

// Push notification handler
self.addEventListener('push', (event) => {
  console.log('[SW] Push Received.');
  
  const title = 'Portfolio Update';
  const options = {
    body: event.data ? event.data.text() : 'Something new on the portfolio!',
    icon: '/static/icons/icon-192x192.png',
    badge: '/static/icons/badge-72x72.png',
    tag: 'portfolio-update',
    vibrate: [200, 100, 200],
    data: {
      dateOfArrival: Date.now(),
      primaryKey: 1
    },
    actions: [
      {
        action: 'explore',
        title: 'View Portfolio',
        icon: '/static/icons/action-icon.png'
      },
      {
        action: 'close',
        title: 'Close',
        icon: '/static/icons/close-icon.png'
      }
    ]
  };
  
  event.waitUntil(self.registration.showNotification(title, options));
});

// Notification click handler
self.addEventListener('notificationclick', (event) => {
  console.log('[SW] Notification click Received.');
  
  event.notification.close();
  
  if (event.action === 'explore') {
    event.waitUntil(clients.openWindow('/'));
  } else if (event.action === 'close') {
    // Just close the notification
  } else {
    // Default action - open the app
    event.waitUntil(clients.openWindow('/'));
  }
});