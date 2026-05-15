import { signInWithPopup } from "firebase/auth";
import { auth, provider } from "../lib/firebase";

export default function Login() {

    const login = async () => {
        await signInWithPopup(auth, provider);
    };

    return (
        <div className="flex h-screen items-center justify-center">

            <button
                onClick={login}
                className="bg-blue-600 text-white px-6 py-3 rounded-lg"
            >
                Login with Google
            </button>

        </div>
    );
}