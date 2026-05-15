import {
    signInWithPopup,
    createUserWithEmailAndPassword,
    signInWithEmailAndPassword
} from "firebase/auth";

import { auth, provider } from "./lib/firebase";


export const loginWithGoogle = async () => {
    try {
        const result = await signInWithPopup(auth, provider);
        return await result.user.getIdToken();
    } catch (err: any) {
        console.error("Google login error:", err);
        throw new Error(err.message);
    }
};


export const registerWithEmail = async (email: string, password: string) => {
    try {
        const result = await createUserWithEmailAndPassword(auth, email, password);
        return await result.user.getIdToken();
    } catch (err: any) {
        console.error("Register error:", err);
        throw new Error(err.message);
    }
};


export const loginWithEmail = async (email: string, password: string) => {
    try {
        const result = await signInWithEmailAndPassword(auth, email, password);
        return await result.user.getIdToken();
    } catch (err: any) {
        console.error("Login error:", err);
        throw new Error(err.message);
    }
};