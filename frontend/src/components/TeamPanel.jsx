import { useEffect, useState } from "react";
import api from "../lib/api";

export default function TeamPanel() {
    const [team, setTeam] = useState(null);
    const [members, setMembers] = useState([]);
    const [invites, setInvites] = useState([]);
    const [email, setEmail] = useState("");
    const [name, setName] = useState("");
    const [role, setRole] = useState("employee");
    const [loading, setLoading] = useState(false);
    const [isOwner, setIsOwner] = useState(false);

    const load = async () => {
        try {
            const t = await api.get("/teams/me");
            setTeam(t.data);

            if (t.data) {

                const me = await api.get("/auth/me");
                setIsOwner(me.data.id === t.data.owner_id);

                const m = await api.get("/teams/members");
                setMembers(m.data);

                const i = await api.get("/teams/invites");
                setInvites(i.data);
            }
        } catch (e) {
            console.error(e);
        }
    };

    useEffect(() => {
        load();
    }, []);

    const invite = async () => {
        if (!email) return;

        try {
            setLoading(true);

            await api.post("/teams/invite", {
                email,
                name,
                role,
            });

            alert("Invitation sent ✅");

            setEmail("");
            setName("");
            setRole("employee");
            load();

        } catch (e) {
            alert(e.response?.data?.detail || "Error sending invitation");
        } finally {
            setLoading(false);
        }
    };

    if (!team) {
        return (
            <div>
                <h2>No team yet</h2>
                <p>Create your team first.</p>
            </div>
        );
    }

    const cancelInvite = async (inviteId) => {
        if (!window.confirm("Cancel this invitation?")) return;

        try {
            await api.delete(`/teams/invite/${inviteId}`);
            alert("Invitation cancelled ✅");
            load();
        } catch (e) {
            alert(e.response?.data?.detail || "Error cancelling invitation");
        }
    };

    const pendingInvites = invites.filter(i => !i.accepted);
    const acceptedInvites = invites.filter(i => i.accepted);

    return (
        <div>
            <h2 style={{ marginBottom: 10 }}>{team.name}</h2>

            <p style={{ color: "#666", marginBottom: 20 }}>
                Invite and manage your team members
            </p>

            {isOwner ? (
                <div style={{
                    display: "flex",
                    gap: 10,
                    marginBottom: 20
                }}>
                    <input
                        placeholder="Full name..."
                        value={name}
                        onChange={(e) => setName(e.target.value)}
                        style={{
                            padding: 10,
                            flex: 1,
                            borderRadius: 6,
                            border: "1px solid #ccc"
                        }}
                    />

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

                    <select
                        value={role}
                        onChange={(e) => setRole(e.target.value)}
                        style={{
                            padding: 10,
                            borderRadius: 6,
                            border: "1px solid #ccc"
                        }}
                    >
                        <option value="employee">Employee</option>
                        <option value="manager">Manager</option>
                    </select>

                    <button
                        onClick={invite}
                        disabled={loading}
                        style={{
                            background: "#3b82f6",
                            color: "white",
                            padding: "10px 15px",
                            borderRadius: 6,
                            border: "none"
                        }}
                    >
                        {loading ? "..." : "Invite"}
                    </button>
                </div>
            ) : (
                <div style={{
                    background: "#eef2ff",
                    color: "#475569",
                    padding: 14,
                    borderRadius: 10,
                    marginBottom: 20
                }}>
                    You are a team member. Only the team owner can invite new people.
                </div>
            )}

            <h3 style={{ marginTop: 30 }}>Pending invitations</h3>

            {pendingInvites.length === 0 && (
                <div style={{ color: "#666", marginBottom: 20 }}>
                    No pending invitations
                </div>
            )}

            {pendingInvites.map(invite => (
                <div
                    key={invite.id}
                    style={{
                        background: "white",
                        padding: 12,
                        marginBottom: 10,
                        borderRadius: 8,
                        display: "flex",
                        justifyContent: "space-between",
                        alignItems: "center"
                    }}
                >
                    <div>
                        <div style={{ fontWeight: 600 }}>
                            {invite.name || "No name"}
                        </div>

                        <div style={{ fontSize: 13, color: "#6b7280" }}>
                            {invite.email}
                        </div>
                        <div style={{ fontSize: 12, color: "#6b7280" }}>
                            Role: {invite.role}
                        </div>
                    </div>

                    <div style={{
                        display: "flex",
                        gap: 8,
                        alignItems: "center"
                    }}>
                        <div style={{
                            fontSize: 12,
                            background: "#fef3c7",
                            color: "#92400e",
                            padding: "4px 8px",
                            borderRadius: 6
                        }}>
                            Not accepted yet
                        </div>

                        {isOwner && (
                            <button
                                onClick={() => cancelInvite(invite.id)}
                                style={{
                                    fontSize: 12,
                                    background: "#fee2e2",
                                    color: "#991b1b",
                                    border: "none",
                                    padding: "5px 9px",
                                    borderRadius: 6,
                                    cursor: "pointer"
                                }}
                            >
                                Cancel
                            </button>
                        )}
                    </div>
                </div>
            ))}

            <h3 style={{ marginTop: 30 }}>Accepted invitations</h3>

            {acceptedInvites.length === 0 && (
                <div style={{ color: "#666", marginBottom: 20 }}>
                    No accepted invitations yet
                </div>
            )}

            {acceptedInvites.map(invite => (
                <div
                    key={invite.id}
                    style={{
                        background: "white",
                        padding: 12,
                        marginBottom: 10,
                        borderRadius: 8,
                        display: "flex",
                        justifyContent: "space-between",
                        alignItems: "center"
                    }}
                >
                    <div>
                        <div style={{ fontWeight: 600 }}>
                            {invite.name || "No name"}
                        </div>

                        <div style={{ fontSize: 13, color: "#6b7280" }}>
                            {invite.email}
                        </div>
                        <div style={{ fontSize: 12, color: "#6b7280" }}>
                            Role: {invite.role}
                        </div>
                    </div>

                    <div style={{
                        fontSize: 12,
                        background: "#dcfce7",
                        color: "#166534",
                        padding: "4px 8px",
                        borderRadius: 6
                    }}>
                        Accepted ✅
                    </div>
                </div>
            ))}

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