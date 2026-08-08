(function () {
  if (!('serviceWorker' in navigator)) return;
  // Desktop/local builds now run without a service worker to avoid stale cached bundles.
  if (window.location && (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')) {
    return;
  }
})();
