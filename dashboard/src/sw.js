// dashboard/src/sw.js
import { precacheAndRoute } from 'workbox-precaching';

// Precache static assets
precacheAndRoute(self.__WB_MANIFEST);

// Handle Push Events
self.addEventListener('push', (event) => {
    let data = { title: 'API Radar Alert', body: 'New activity detected.' };
    if (event.data) {
        try {
            data = event.data.json();
        } catch (e) {
            data.body = event.data.text();
        }
    }

    const options = {
        body: data.body,
        icon: '/icon-192.png',
        badge: '/icon-192.png',
        vibrate: [200, 100, 200],
        data: {
            url: self.location.origin
        }
    };

    event.waitUntil(
        self.registration.showNotification(data.title, options)
    );
});

// Handle Notification Click
self.addEventListener('notificationclick', (event) => {
    event.notification.close();
    event.waitUntil(
        clients.openWindow(event.notification.data.url)
    );
});
