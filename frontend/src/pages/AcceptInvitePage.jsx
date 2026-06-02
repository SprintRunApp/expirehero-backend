import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import api from "../lib/api";

export default function AcceptInvitePage() {
    const { token } = useParams();

    const [invite, setInvite] = useState(null);
    const [loading, setLoading] = useState(true);
    const [accepted, setAccepted] = useState(false);
    const [error, setError] = useState("");

    useEffect(() => {
        loadInvite();
    }, []);

    const loadInvite = async () => {
        try {
            const res = await api.get(`/teams/invite/${token}`);
            setInvite(res.data);
        } catch (e) {
            setError(
                e.response?.data?.detail || "Invalid invitation"
            );
        } finally {
            setLoading(false);
        }
    };

    const acceptInvite = async () => {
        try {
            await api.post(`/teams/invite/${token}/accept`);

            setAccepted(true);

        } catch (e) {
            alert(
                e.response?.data?.detail || "Cannot accept invitation"
            );
        }
    };

    if (loading) {
        return <div style={{ padding: 40 }}>Loading...</div>;
    }

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
                <p>You can now use ExpireHeros with your team.</p>
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
                width: 420,
                boxShadow: "0 20px 50px rgba(0,0,0,0.08)"
            }}>
                <h2 style={{ marginBottom: 20 }}>
                    Team Invitation
                </h2>

                <div style={{ marginBottom: 12 }}>
                    <strong>Team:</strong> {invite.team_name}
                </div>

                <div style={{ marginBottom: 12 }}>
                    <strong>Email:</strong> {invite.email}
                </div>

                <div style={{ marginBottom: 30 }}>
                    <strong>Role:</strong> {invite.role}
                </div>

                <button
                    onClick={acceptInvite}
                    style={{
                        width: "100%",
                        padding: 14,
                        borderRadius: 10,
                        border: "none",
                        background: "#2563eb",
                        color: "white",
                        fontWeight: 600,
                        cursor: "pointer"
                    }}
                >
                    Accept invitation
                </button>
            </div>
        </div>
    );
}