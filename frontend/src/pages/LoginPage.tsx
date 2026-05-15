import { useState } from "react";
import {
    loginWithGoogle,
    loginWithEmail,
    registerWithEmail
} from "../auth";

export default function LoginPage({ onLogin }) {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [company, setCompany] = useState("");
    const [fullName, setFullName] = useState("");

    const callBackend = async (
        token: string,
        fullName: string | null,
        company: string | null
    ) => {
        try {
            const res = await fetch(`${import.meta.env.VITE_API_URL}/api/auth/me`, {
                method: "POST",
                headers: {
                    Authorization: `Bearer ${token}`,
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    full_name: fullName,
                    company_name: company
                })
            });

            console.log("RESPONSE STATUS:", res.status);

            if (!res.ok) {
                const text = await res.text();
                console.error("BACKEND ERROR:", text);
                alert("Backend error");
                return;
            }

            const user = await res.json();

            console.log("USER FROM BACKEND:", user);

            localStorage.setItem("token", token);

            onLogin(user);

        } catch (e) {
            console.error("CALL BACKEND ERROR:", e);
            alert("Network error");
        }
    };

    return (
        <div style={{
            height: "100vh",
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            flexDirection: "column",
            gap: 10
        }}>
            <h2>ExpireHero</h2>

            {/* 🔥 COMPANY */}
            <input
                placeholder="Company name"
                value={company}
                onChange={(e) => setCompany(e.target.value)}
            />

            {/* 🔥 FULL NAME */}
            <input
                placeholder="Full name"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
            />

            {/* EMAIL */}
            <input
                placeholder="Email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
            />

            {/* PASSWORD */}
            <input
                placeholder="Password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
            />

            {/* REGISTER */}
            <button onClick={async () => {
                try {
                    // 🔥 WALIDACJA NAJPIERW
                    if (!fullName || !company) {
                        alert("Enter full name and company");
                        return;
                    }

                    console.log("REGISTER CLICK");

                    const token = await registerWithEmail(email, password);

                    console.log("TOKEN:", token);

                    await callBackend(token, fullName, company);

                } catch (e) {
                    console.error("REGISTER ERROR:", e);
                    alert(e.message);
                }
            }}>
                Register
            </button>

            {/* LOGIN */}
            <button onClick={async () => {
                try {
                    console.log("LOGIN CLICK");

                    const token = await loginWithEmail(email, password);

                    console.log("TOKEN:", token);

                    // 🔥 NIE NADPISUJEMY danych
                    await callBackend(token, null, null);

                } catch (e) {
                    console.error("LOGIN ERROR:", e);
                    alert(e.message);
                }
            }}>
                Login
            </button>

            {/* GOOGLE */}
            <button onClick={async () => {
                try {
                    console.log("GOOGLE CLICK");

                    const token = await loginWithGoogle();

                    console.log("TOKEN:", token);

                    await callBackend(token, null, null);

                } catch (e) {
                    console.error("GOOGLE ERROR:", e);
                    alert(e.message);
                }
            }}>
                Google Login
            </button>
        </div>
    );
}