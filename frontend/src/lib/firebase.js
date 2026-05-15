import { initializeApp } from "firebase/app";
import {
    getAuth,
    GoogleAuthProvider,
    createUserWithEmailAndPassword,
    signInWithEmailAndPassword
} from "firebase/auth";

const firebaseConfig = {
    apiKey: "AIzaSyAMxgHr16w1nn5uOdUHecwcuZFHAOHAZd0",
    authDomain: "expirehero.firebaseapp.com",
    projectId: "expirehero",
    storageBucket: "expirehero.firebasestorage.app",
    messagingSenderId: "396999291040",
    appId: "1:396999291040:web:d0773a8af947761da799c5"
};

const app = initializeApp(firebaseConfig);

export const auth = getAuth(app);
export const provider = new GoogleAuthProvider();

export {
    createUserWithEmailAndPassword,
    signInWithEmailAndPassword
};