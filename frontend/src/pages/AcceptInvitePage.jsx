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
        await fetch(`${import.meta.env.VITE_API_URL}/api/auth/me`, {
            method: "POST",
            headers: {
                Authorization: `Bearer ${firebaseToken}`,
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                full_name: invite.name,
                company_name: null
            })
        });
    };

    const finishInvite = async (firebaseToken) => {
        localStorage.setItem("token", firebaseToken);

        await api.post(`/teams/invite/${token}/accept`);

        setAccepted(true);

        setTimeout(() => {
            window.location.href = "/";
        }, 1200);
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
            background: "#f8fafc"
        }}>
            <div style={{
                background: "white",
                padding: 40,
                borderRadius: 20,
                width: 440,
                boxShadow: "0 20px 50px rgba(0,0,0,0.08)"
            }}>
                <h2 style={{ marginBottom: 20 }}>Accept Team Invitation</h2>

                <ReadonlyInput label="Company" value={invite.team_name} />
                <ReadonlyInput label="Full name" value={invite.name || ""} />
                <ReadonlyInput label="Email" value={invite.email} />
                <ReadonlyInput label="Role" value={invite.role} />

                <input
                    type="password"
                    placeholder={mode === "register" ? "Create password" : "Password"}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    style={inputStyle}
                />

                <button
                    onClick={mode === "register" ? handleRegister : handleLogin}
                    disabled={busy}
                    style={{
                        width: "100%",
                        padding: 14,
                        borderRadius: 10,
                        border: "none",
                        background: "#2563eb",
                        color: "white",
                        fontWeight: 600,
                        cursor: "pointer",
                        marginTop: 10
                    }}
                >
                    {busy
                        ? "Please wait..."
                        : mode === "register"
                            ? "Create account & accept"
                            : "Sign in & accept"}
                </button>

                <div style={{
                    marginTop: 20,
                    textAlign: "center",
                    color: "#64748b",
                    fontSize: 14
                }}>
                    {mode === "register" ? "Already have an account? " : "Need to create account? "}

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
    padding: "14px 16px",
    borderRadius: 12,
    border: "1px solid #dbeafe",
    marginBottom: 14,
    fontSize: 15
};