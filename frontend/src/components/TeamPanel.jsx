import { useEffect, useState } from "react";
import api from "../lib/api";

export default function TeamPanel() {
    const [team, setTeam] = useState(null);
    const [members, setMembers] = useState([]);
    const [email, setEmail] = useState("");
    const [loading, setLoading] = useState(false);

    const load = async () => {
        try {
            const t = await api.get("/teams/me");
            setTeam(t.data);

            if (t.data) {
                const m = await api.get("/teams/members");
                setMembers(m.data);
            }
        } catch (e) {
            console.error(e);
        }
    };

    useEffect(() => {
        load();
    }, []);

    const add = async () => {
        if (!email) return;

        try {
            setLoading(true);

            await api.post("/teams/add-member", { email });

            setEmail("");
            load();

        } catch (e) {
            alert(e.response?.data?.detail || "Error adding user");
        } finally {
            setLoading(false);
        }
    };

    // ❌ brak teamu
    if (!team) {
        return (
            <div>
                <h2>No team yet</h2>
                <p>Create your team first (coming next step 👇)</p>
            </div>
        );
    }

    return (
        <div>
            {/* TEAM HEADER */}
            <h2 style={{ marginBottom: 10 }}>{team.name}</h2>

            <p style={{ color: "#666", marginBottom: 20 }}>
                Manage your team members
            </p>

            {/* ADD MEMBER */}
            <div style={{
                display: "flex",
                gap: 10,
                marginBottom: 20
            }}>
                <input
                    placeholder="Enter email..."
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    style={{
                        padding: 10,
                        flex: 1,
                        borderRadius: 6,
                        border: "1px solid #ccc"
                    }}
                />

                <button
                    onClick={add}
                    disabled={loading}
                    style={{
                        background: "#3b82f6",
                        color: "white",
                        padding: "10px 15px",
                        borderRadius: 6,
                        border: "none"
                    }}
                >
                    {loading ? "..." : "Add"}
                </button>
            </div>

            {/* MEMBERS LIST */}
            <h3>Members</h3>

            {members.length === 0 && (
                <div style={{ color: "#666" }}>
                    No members yet
                </div>
            )}

            {members.map(m => (
                <div key={m.id} style={{
                    background: "white",
                    padding: 12,
                    marginBottom: 10,
                    borderRadius: 8,
                    display: "flex",
                    justifyContent: "space-between"
                }}>
                    <div>{m.email}</div>

                    <div style={{
                        fontSize: 12,
                        background: "#e0e7ff",
                        padding: "4px 8px",
                        borderRadius: 6
                    }}>
                        {m.role}
                    </div>
                </div>
            ))}
        </div>
    );
}