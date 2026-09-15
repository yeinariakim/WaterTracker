importScripts('https://www.gstatic.com/firebasejs/10.12.2/firebase-app-compat.js');
importScripts('https://www.gstatic.com/firebasejs/10.12.2/firebase-messaging-compat.js');

firebase.initializeApp({
  apiKey: "AIzaSyDr4oe97AD-L9QeBQ6epPG9Pa4Bo64ArGA",
  authDomain: "waterttracker.firebaseapp.com",
  projectId: "waterttracker",
  storageBucket: "waterttracker.firebasestorage.app",
  messagingSenderId: "386879740854",
  appId: "1:386879740854:web:5d07d48a1f0d22b5c4bf17"
});

const messaging = firebase.messaging();

messaging.onBackgroundMessage((payload) => {
  const title = (payload.notification && payload.notification.title) || '💧 물 마실 시간이에요';
  const body = (payload.notification && payload.notification.body) || '';
  self.registration.showNotification(title, { body });
});
