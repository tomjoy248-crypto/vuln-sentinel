(function () {
  if (!('serviceWorker' in navigator)) return;

  var CACHE_PREFIX = 'vuln-sentinel-v11-s';
  var CACHE_BUSTER = 'v4';
  var CURRENT_CACHE = CACHE_PREFIX + '-' + CACHE_BUSTER;
  var SHOULD_SKIP_SW = false;

  try {
    var host = window.location && window.location.hostname ? window.location.hostname : '';
    SHOULD_SKIP_SW = host === 'localhost' || host === '127.0.0.1' || !!window.__TAURI__ || !!window.__TAURI_INTERNALS__;
  } catch (e) {}

  function clearOldCaches() {
    if (!window.caches || !caches.keys) return Promise.resolve();
    return caches.keys().then(function(keys) {
      return Promise.all(keys.filter(function(key) {
        return key.indexOf(CACHE_PREFIX) === 0 && key !== CURRENT_CACHE;
      }).map(function(key) {
        return caches.delete(key);
      }));
    });
  }

  function unregisterOldServiceWorkers() {
    return navigator.serviceWorker.getRegistrations().then(function(registrations) {
      return Promise.all(registrations.map(function(registration) {
        return registration.unregister();
      }));
    }).catch(function() {
      return Promise.resolve();
    });
  }

  function primeCleanState() {
    return clearOldCaches().then(unregisterOldServiceWorkers).catch(function() {});
  }

  window.addEventListener('load', function () {
    primeCleanState().finally(function() {
      if (SHOULD_SKIP_SW) {
        console.log('[PWA] Skipping service worker for desktop/local use');
        return;
      }
      navigator.serviceWorker.register('/sw.js')
        .then(function (registration) {
          console.log('[PWA] ServiceWorker registered:', registration.scope);
        })
        .catch(function (err) {
          console.error('[PWA] ServiceWorker registration failed:', err);
        });
    });
  });
})();
