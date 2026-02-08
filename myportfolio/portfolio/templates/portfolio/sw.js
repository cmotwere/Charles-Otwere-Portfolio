// Service Worker for {{ pwa_data.app_name }}
const CACHE_NAME = 'portfolio-v1';
const OFFLINE_URL = '/static/offline.html';

// Files to cache for offline functionality
const FILES_TO_CACHE = [
  '/',
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

// Fetch event - serve cached content when offline
self.addEventListener('fetch', (event) => {
  console.log('[SW] Fetch', event.request.url);
  
  // Skip non-GET requests
  if (event.request.method !== 'GET') return;
  
  // Skip API requests
  if (event.request.url.includes('/api/')) return;
  
  event.respondWith(
    caches.open(CACHE_NAME)
      .then((cache) => {
        return cache.match(event.request)
          .then((response) => {
            if (response) {
              console.log('[SW] Serving from cache: ', event.request.url);
              return response;
            }
            
            // Fetch from network
            return fetch(event.request)
              .then((response) => {
                // Don't cache non-successful responses
                if (!response || response.status !== 200 || response.type !== 'basic') {
                  return response;
                }
                
                // Clone the response
                const responseToCache = response.clone();
                
                // Cache certain types of requests
                if (event.request.url.includes('/static/') || 
                    event.request.url.match(/\.(css|js|png|jpg|jpeg|svg|woff|woff2)$/)) {
                  cache.put(event.request, responseToCache);
                }
                
                return response;
              })
              .catch(() => {
                // If network fails, serve offline page for navigation requests
                if (event.request.mode === 'navigate') {
                  return cache.match(OFFLINE_URL);
                }
              });
          });
      })
  );
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