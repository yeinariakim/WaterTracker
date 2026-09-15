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

// firebase.messaging()을 초기화하면, 알림(notification) 필드가 있는 푸시는
// 라이브러리가 알아서 한 번만 표시해줘요. 여기서 직접 showNotification을
// 또 호출하면 중복으로 두 번 뜨기 때문에, 별도 핸들러는 추가하지 않아요.
firebase.messaging();
