(function () {
  if (!('serviceWorker' in navigator)) return;
  window.addEventListener('load', function () {
    navigator.serviceWorker.register('/sw.js')
      .then(function (registration) {
        console.log('[PWA] ServiceWorker registered:', registration.scope);
      })
      .catch(function (err) {
        console.error('[PWA] ServiceWorker registration failed:', err);
      });
  });
})();
