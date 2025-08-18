// Cache Management Utilities
// Extracted from index.html for better maintainability

// Force cache clear for development
if ('serviceWorker' in navigator) {
    navigator.serviceWorker.getRegistrations().then(function(registrations) {
        for(let registration of registrations) {
            registration.unregister();
        }
    });
}

// Clear all caches
if ('caches' in window) {
    caches.keys().then(function(names) {
        for (let name of names) {
            caches.delete(name);
        }
    });
}

console.log('🧹 NOCACHE VERSION 235500 - Force reload everything!');

// Force complete page reload after cache clear
setTimeout(function() {
    if (window.location.search.indexOf('nocache') === -1) {
        window.location.href = window.location.href + '?nocache=' + Date.now();
    }
}, 100);

console.log('✅ [EMBEDDED] Cache Management utilities loaded');