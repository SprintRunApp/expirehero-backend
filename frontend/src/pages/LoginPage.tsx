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
    const [mode, setMode] = useState("register");

    const callBackend = async (token, fullNameValue, companyValue) => {
        try {
            const res = await fetch(`${import.meta.env.VITE_API_URL}/api/auth/me`, {
                method: "POST",
                headers: {
                    Authorization: `Bearer ${token}`,
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    full_name: fullNameValue,
                    company_name: companyValue
                })
            });

            if (!res.ok) {
                const text = await res.text();
                console.error("BACKEND ERROR:", text);
                alert("Backend error");
                return;
            }

            const user = await res.json();
            localStorage.setItem("token", token);
            onLogin(user);

        } catch (e) {
            console.error("CALL BACKEND ERROR:", e);
            alert("Network error");
        }
    };

    const handleRegister = async () => {
        try {
            if (!fullName || !company || !email || !password) {
                alert("Fill in all fields");
                return;
            }

            const token = await registerWithEmail(email, password);
            await callBackend(token, fullName, company);

        } catch (e) {
            console.error("REGISTER ERROR:", e);
            alert(e.message);
        }
    };

    const handleLogin = async () => {
        try {
            if (!email || !password) {
                alert("Enter email and password");
                return;
            }

            const token = await loginWithEmail(email, password);
            await callBackend(token, null, null);

        } catch (e) {
            console.error("LOGIN ERROR:", e);
            alert(e.message);
        }
    };

    const handleGoogle = async () => {
        try {
            const token = await loginWithGoogle();
            await callBackend(token, null, null);

        } catch (e) {
            console.error("GOOGLE ERROR:", e);
            alert(e.message);
        }
    };

    return (
        <div style={{
            minHeight: "100vh",
            width: "100%",
            background: "linear-gradient(135deg, #dbeafe, #eff6ff)",
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            padding: 24,
            fontFamily: "Inter, sans-serif"
        }}>
            <div style={{
                width: "100%",
                maxWidth: 1180,
                minHeight: 620,
                display: "flex",
                overflow: "hidden",
                borderRadius: 28,
                background: "rgba(255,255,255,0.75)",
                backdropFilter: "blur(20px)",
                boxShadow: `
                    0 25px 60px rgba(37,99,235,0.18),
                    0 0 80px rgba(96,165,250,0.12)
                `
            }}>

                {/* LEFT BRAND PANEL */}
                <div style={{
                    flex: 1,
                    padding: 56,
                    background: "linear-gradient(145deg, rgba(191,219,254,0.9), rgba(96,165,250,0.75))",
                    color: "#0f172a",
                    position: "relative",
                    overflow: "hidden"
                }}>
                    <img
                        src="/logo.png"
                        style={{
                            height: 48,
                            marginBottom: 70,
                            filter: "drop-shadow(0 6px 14px rgba(0,0,0,0.22))"
                        }}
                    />

                    <h1 style={{
                        fontSize: 42,
                        lineHeight: 1.1,
                        margin: 0,
                        marginBottom: 20,
                        letterSpacing: "-1px"
                    }}>
                        Stay ahead of<br />expiration dates.
                    </h1>

                    <p style={{
                        fontSize: 17,
                        lineHeight: 1.6,
                        color: "#334155",
                        maxWidth: 420,
                        marginBottom: 36
                    }}>
                        Track certificates, manage inspections and never miss what matters.
                    </p>

                    <Feature title="Track" text="Keep all important company items in one place." />
                    <Feature title="Manage" text="Set reminders and stay always up to date." />
                    <Feature title="Never Miss" text="Get notified before anything expires." />


                    <div style={{
                        position: "absolute",
                        width: 240,
                        height: 240,
                        borderRadius: "50%",
                        background: "rgba(96,165,250,0.25)",
                        filter: "blur(80px)",
                        bottom: -60,
                        left: -60
                    }} />

                    <div style={{
                        position: "absolute",
                        width: 120,
                        height: 120,
                        borderRadius: "50%",
                        background: "rgba(255,255,255,0.25)",
                        filter: "blur(50px)",
                        top: 120,
                        right: 40
                    }} />

                    <div style={{
                        position: "absolute",
                        width: 6,
                        height: 6,
                        borderRadius: "50%",
                        background: "white",
                        top: 180,
                        left: 320,
                        boxShadow: "0 0 18px rgba(255,255,255,0.9)"
                    }} />

                    <div style={{
                        position: "absolute",
                        width: 4,
                        height: 4,
                        borderRadius: "50%",
                        background: "#ffffff",
                        bottom: 140,
                        right: 120,
                        boxShadow: "0 0 14px rgba(255,255,255,0.9)"
                    }} />


                </div>

                {/* RIGHT FORM PANEL */}
                <div style={{
                    flex: 1,
                    padding: 64,
                    display: "flex",
                    justifyContent: "center",
                    alignItems: "center"
                }}>
                    <div style={{
                        width: "100%",
                        maxWidth: 460
                    }}>
                        <h2 style={{
                            fontSize: 30,
                            marginBottom: 8,
                            color: "#0f172a"
                        }}>
                            {mode === "register" ? "Create your account" : "Welcome back"}
                        </h2>

                        <p style={{
                            color: "#64748b",
                            marginBottom: 32
                        }}>
                            {mode === "register"
                                ? "Start managing important deadlines with ExpireHeros."
                                : "Sign in to continue to your dashboard."}
                        </p>

                        {mode === "register" && (
                            <>
                                <Input label="Company name" value={company} onChange={setCompany} />
                                <Input label="Full name" value={fullName} onChange={setFullName} />
                            </>
                        )}

                        <Input label="Email address" value={email} onChange={setEmail} />
                        <Input label="Password" value={password} onChange={setPassword} type="password" />

                        <button
                            onClick={mode === "register" ? handleRegister : handleLogin}
                            style={primaryButton}
                        >
                            {mode === "register" ? "Create account" : "Sign in"}
                        </button>

                        <div style={{
                            display: "flex",
                            alignItems: "center",
                            gap: 12,
                            margin: "24px 0",
                            color: "#94a3b8",
                            fontSize: 14
                        }}>
                            <div style={{ flex: 1, height: 1, background: "#e2e8f0" }} />
                            or
                            <div style={{ flex: 1, height: 1, background: "#e2e8f0" }} />
                        </div>

                        <button
                            onClick={handleGoogle}
                            style={googleButton}
                        >
                            Continue with Google
                        </button>

                        <div style={{
                            marginTop: 28,
                            textAlign: "center",
                            color: "#64748b",
                            fontSize: 14
                        }}>
                            {mode === "register" ? "Already have an account? " : "Don't have an account? "}

                            <span
                                onClick={() => setMode(mode === "register" ? "login" : "register")}
                                style={{
                                    color: "#2563eb",
                                    cursor: "pointer",
                                    fontWeight: 600
                                }}
                            >
                                {mode === "register" ? "Sign in" : "Create account"}
                            </span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

function Feature({ title, text }) {
    return (
        <div style={{
            display: "flex",
            gap: 14,
            marginBottom: 22,
            alignItems: "flex-start"
        }}>
            <div style={{
                width: 42,
                height: 42,
                borderRadius: 14,
                background: "rgba(255,255,255,0.55)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                color: "#2563eb",
                fontWeight: 800,
                boxShadow: "0 8px 18px rgba(37,99,235,0.18)"
            }}>
                ✓
            </div>

            <div>
                <div style={{ fontWeight: 700, marginBottom: 4 }}>{title}</div>
                <div style={{ color: "#334155", fontSize: 14, lineHeight: 1.4 }}>{text}</div>
            </div>
        </div>
    );
}

function Input({ label, value, onChange, type = "text" }) {
    return (
        <div style={{ marginBottom: 16 }}>
            <input
                type={type}
                placeholder={label}
                value={value}
                onChange={(e) => onChange(e.target.value)}
                style={{
                    width: "100%",
                    boxSizing: "border-box",
                    background: "#f8fbff",
                    border: "1px solid #dbeafe",
                    borderRadius: 14,
                    padding: "15px 16px",
                    fontSize: 15,
                    outline: "none",
                    color: "#0f172a",
                    boxShadow: "inset 0 1px 1px rgba(255,255,255,0.8)"
                }}
            />
        </div>
    );
}

const primaryButton = {
    width: "100%",
    marginTop: 8,
    padding: "15px 18px",
    borderRadius: 999,
    border: "none",
    background: "linear-gradient(135deg, #3b82f6, #60a5fa)",
    color: "white",
    fontWeight: 700,
    fontSize: 16,
    cursor: "pointer",
    boxShadow: `
        0 12px 30px rgba(59,130,246,0.4),
        inset 0 1px 1px rgba(255,255,255,0.4)
    `
};

const googleButton = {
    width: "100%",
    padding: "14px 18px",
    borderRadius: 14,
    border: "1px solid #dbeafe",
    background: "white",
    color: "#0f172a",
    fontWeight: 600,
    fontSize: 15,
    cursor: "pointer"
};