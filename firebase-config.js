// firebase-config.js
import { initializeApp } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-app.js";
import { getFirestore, collection, addDoc, query, orderBy, limit, onSnapshot } 
       from "https://www.gstatic.com/firebasejs/10.7.1/firebase-firestore.js";
import { getAuth, signInWithEmailAndPassword, createUserWithEmailAndPassword, 
         signOut, onAuthStateChanged } 
       from "https://www.gstatic.com/firebasejs/10.7.1/firebase-auth.js";

// ⚠️ ضع بيانات مشروعك هنا من Firebase Console > Project Settings
const firebaseConfig = {
  apiKey: