import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import api from "../lib/api";
import { registerWithEmail, loginWithEmail } from "../auth";

export default function AcceptInvitePage() {

    console.log("🔥 ACCEPT INVITE COMPONENT LOADED");
    
    const { token } = useParams();

    const [invite, setInvite] = useState(null);
    const [password, setPassword] = useState("");
    const [mode, setMode] = useState("register");
    const [loading, setLoading] = useState(true);
    const [busy, setBusy] = useState(false);
    const [accepted, setAccepted] = useState(false);
    const [error, setError] = useState("");
    const [notice, setNotice] = useState("");

    const loadInvite = async () => {
        console.log("🔥 LOAD INVITE STARTED");

        try {
            const res = await api.get(`/teams/invite/${token}`);

            console.log("INVITE DATA:", res.data);
            alert(JSON.stringify(res.data, null, 2));

            setInvite(res.data);
        } catch (e) {
            console.error("LOAD INVITE ERROR:", e);
            setError(e.response?.data?.detail || "Invalid invitation");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadInvite();
    }, [token]);

    const createBackendProfile = async (firebaseToken) => {
        console.log("API URL:", import.meta.env.VITE_API_URL);
        console.log("CREATE BACKEND PROFILE STARTED");

        const res = await fetch(`${import.meta.env.VITE_API_URL}/api/auth/me`, {
            method: "POST",
            headers: {
                Authorization: `Bearer ${firebaseToken}`,
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                full_name: invite.name
            })
        });

        console.log("AUTH ME STATUS:", res.status);
        console.log("AUTH ME TEXT:", await res.clone().text());

        if (!res.ok) {
            throw new Error("Backend profile creation failed");
        }

        return await res.json();
    };

    const finishInvite = async (firebaseToken) => {
        localStorage.setItem("token", firebaseToken);

        try {
            const res = await api.post(`/teams/invite/${token}/accept`);
            console.log("ACCEPT INVITE RESPONSE:", res.data);

            setAccepted(true);

            setTimeout(() => {
                window.location.href = "/";
            }, 1200);
        } catch (e) {
            console.error("ACCEPT INVITE ERROR:", e);
            console.error("STATUS:", e.response?.status);
            console.error("DATA:", e.response?.data);
            alert(JSON.stringify(e.response?.data, null, 2));
        }
    };

    const handleRegister = async () => {
        if (!password) {
            alert("Enter password");
            return;
        }

        try {
            setBusy(true);

            const firebaseToken = await registerWithEmail(invite.email, password);

            await createBackendProfile(firebaseToken);
            await finishInvite(firebaseToken);

        } catch (e) {
            console.error(e);

                if (e.code === "auth/email-already-in-use" || e.message?.includes("email-already-in-use")) {
                setNotice("This email already has an account. Please use “Sign in & accept”.");
                setMode("login");
                return;
            }

            alert(e.message || "Cannot create account");
        } finally {
            setBusy(false);
        }   
    };

    const handleLogin = async () => {
        if (!password) {
            alert("Enter password");
            return;
        }

        try {
            setBusy(true);

            const firebaseToken = await loginWithEmail(invite.email, password);

            await createBackendProfile(firebaseToken);
            await finishInvite(firebaseToken);

        } catch (e) {
            console.error(e);
            alert(e.message || "Cannot sign in");
        } finally {
            setBusy(false);
        }
    };

    if (loading) return <div style={{ padding: 40 }}>Loading...</div>;

    if (error) {
        return (
            <div style={{ padding: 40 }}>
                <h2>{error}</h2>
            </div>
        );
    }

    if (accepted) {
        return (
            <div style={{ padding: 40 }}>
                <h2>✅ Invitation accepted</h2>
                <p>Redirecting to dashboard...</p>
            </div>
        );
    }

    return (
        <div style={{
            minHeight: "100vh",
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            background:
                "linear-gradient(135deg, #eef5ff 0%, #dbeafe 100%)",
            padding: 30
        }}>
            <div style={{
                width: 1100,
                maxWidth: "95%",
                minHeight: 700,
                background: "white",
                borderRadius: 28,
                overflow: "hidden",
                display: "flex",
                boxShadow:
                    "0 30px 80px rgba(59,130,246,0.18)"
            }}>

                {/* LEFT PANEL */}
                <div style={{
                    width: "42%",
                    position: "relative",
                    overflow: "hidden",
                    padding: 50,
                    background:
                        "linear-gradient(145deg,#dbeafe 0%,#93c5fd 100%)"
                }}>

                    <img
                        src="/logo.png"
                        style={{
                            width: 260,
                            marginBottom: 70
                        }}
                    />

                    <h1 style={{
                        fontSize: 48,
                        lineHeight: 1.15,
                        margin: 0,
                        color: "#0f172a"
                    }}>
                        You've been invited
                        <br />
                        to join
                        <br />
                        <span style={{
                            color: "#2563eb"
                        }}>
                            {invite.team_name}
                        </span>
                    </h1>

                    <p style={{
                        marginTop: 24,
                        fontSize: 18,
                        lineHeight: 1.7,
                        color: "#475569",
                        maxWidth: 320
                    }}>
                        Complete your account and start
                        collaborating with your team.
                    </p>

                    {/* Glow */}
                    <div style={{
                        position: "absolute",
                        width: 260,
                        height: 260,
                        borderRadius: "50%",
                        background: "rgba(255,255,255,0.35)",
                        filter: "blur(80px)",
                        bottom: -60,
                        left: -60
                    }} />

                    {/* Sparkles */}
                    <div style={{
                        position: "absolute",
                        top: 120,
                        right: 90,
                        width: 6,
                        height: 6,
                        borderRadius: "50%",
                        background: "#fff",
                        boxShadow: "0 0 20px white"
                    }} />

                    <div style={{
                        position: "absolute",
                        top: 220,
                        right: 140,
                        width: 4,
                        height: 4,
                        borderRadius: "50%",
                        background: "#fff",
                        boxShadow: "0 0 12px white"
                    }} />

                </div>

                {/* RIGHT PANEL */}
                <div style={{
                    flex: 1,
                    padding: "60px"
                }}>

                    <div style={{
                        display: "inline-flex",
                        padding: "10px 18px",
                        borderRadius: 999,
                        background: "#eff6ff",
                        color: "#2563eb",
                        fontWeight: 600,
                        marginBottom: 24
                    }}>
                        Employee Invitation
                    </div>

                    <h1 style={{
                        margin: 0,
                        fontSize: 46,
                        color: "#0f172a"
                    }}>
                        Accept Team Invitation
                    </h1>

                    <p style={{
                        marginTop: 16,
                        marginBottom: 30,
                        color: "#64748b",
                        fontSize: 18
                    }}>
                        You've been invited by
                        <strong> {invite.team_name}</strong>
                        {" "}as{" "}
                        <strong>{invite.role}</strong>.
                    </p>

                    <ReadonlyInput
                        label="Company"
                        value={invite.team_name}
                    />

                    <ReadonlyInput
                        label="Full name"
                        value={invite.name || ""}
                    />

                    <ReadonlyInput
                        label="Email"
                        value={invite.email}
                    />

                    <ReadonlyInput
                        label="Role"
                        value={invite.role}
                    />

                    <input
                        type="password"
                        placeholder={
                            mode === "register"
                                ? "Create password"
                                : "Password"
                        }
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        style={{
                            ...inputStyle,
                            height: 64,
                            borderRadius: 18
                        }}
                    />

                    {notice && (
                        <div style={{
                            background: "#eff6ff",
                            color: "#1d4ed8",
                            padding: "12px 16px",
                            borderRadius: 12,
                            marginBottom: 14,
                            border: "1px solid #bfdbfe"
                        }}>
                            {notice}
                        </div>
                    )}

                    <button
                        onClick={
                            mode === "register"
                                ? handleRegister
                                : handleLogin
                        }
                        disabled={busy}
                        style={{
                            width: "100%",
                            height: 58,
                            borderRadius: 999,
                            border: "none",
                            cursor: "pointer",
                            color: "white",
                            fontWeight: 700,
                            fontSize: 17,
                            marginTop: 10,
                            background:
                                "linear-gradient(90deg,#3b82f6,#60a5fa)",
                            boxShadow:
                                "0 10px 30px rgba(59,130,246,0.35)"
                        }}
                    >
                        {busy
                            ? "Please wait..."
                            : mode === "register"
                                ? "Create account & join team"
                                : "Sign in & join team"}
                    </button>

                    <div style={{
                        marginTop: 24,
                        textAlign: "center",
                        color: "#64748b"
                    }}>
                        {mode === "register"
                            ? "Already have an account? "
                            : "Need to create account? "}

                        <span
                            onClick={() => {
                                setNotice("");
                                setMode(
                                    mode === "register"
                                        ? "login"
                                        : "register"
                                );
                            }}
                            style={{
                                color: "#2563eb",
                                fontWeight: 600,
                                cursor: "pointer"
                            }}
                        >
                            {mode === "register"
                                ? "Sign in"
                                : "Create account"}
                        </span>
                    </div>

                </div>

            </div>
        </div>
    );
}

function ReadonlyInput({ label, value }) {
    return (
        <input
            value={value}
            readOnly
            placeholder={label}
            style={{
                ...inputStyle,
                background: "#f1f5f9",
                color: "#475569"
            }}
        />
    );
}

const inputStyle = {
    width: "100%",
    boxSizing: "border-box",
    padding: "18px 20px",
    borderRadius: 18,
    border: "1px solid #dbeafe",
    marginBottom: 16,
    fontSize: 16,
    background: "#ffffff",
    color: "#334155"
};