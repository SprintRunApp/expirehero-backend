import { useEffect, useState } from "react";
import api from "../lib/api";
import QuickReminder from "../components/QuickReminder";
import TeamPanel from "../components/TeamPanel";
import SettingsPanel from "../components/SettingsPanel";

/* ---------------- HELPERS ---------------- */

function getStatus(dueDate) {
    const now = new Date();
    const due = new Date(dueDate);

    now.setHours(0, 0, 0, 0);
    due.setHours(0, 0, 0, 0);

    const diff = Math.ceil((due - now) / (1000 * 60 * 60 * 24));

    if (diff < 0) return "expired";
    if (diff <= 7) return "urgent";
    if (diff <= 30) return "soon";
    return "active";
}

function formatDate(date) {
    return new Date(date).toLocaleDateString();
}

/* ---------------- MAIN ---------------- */

export default function Dashboard({ user }) {
    const [items, setItems] = useState([]);
    const [showForm, setShowForm] = useState(false);
    const [view, setView] = useState("dashboard");

    const load = async () => {
        const res = await api.get("/reminders/");
        setItems(res.data);
    };

    useEffect(() => {
        load();
    }, []);

    const remove = async (id) => {
        if (!confirm("Delete this reminder?")) return;
        await api.delete(`/reminders/${id}`);
        load();
    };

    const edit = async (reminder) => {
        const newDate = prompt("New date (YYYY-MM-DD)", reminder.due_date);
        if (!newDate) return;

        await api.put(`/reminders/${reminder.id}`, {
            due_date: newDate,
        });

        load();
    };

    const expiringSoon = items.filter(r => {
        const status = getStatus(r.due_date);
        return status === "soon" || status === "urgent";
    });

    const expired = items.filter(r => {
        return getStatus(r.due_date) === "expired";
    });

    return (
        <div style={{
            minHeight: "100vh",
            width: "100%",
            background: "linear-gradient(135deg, #dbeafe, #eff6ff)",
            display: "flex",
            justifyContent: "center",
            padding: "60px 20px"
        }}>

            {/* APP CONTAINER */}
            <div style={{
                width: "100%",
                maxWidth: 1200,
                borderRadius: 24,
                overflow: "hidden",
                display: "flex",
                background: "rgba(255,255,255,0.7)",
                backdropFilter: "blur(20px)",
                boxShadow: "0 30px 80px rgba(37,99,235,0.25)"
            }}>

                {/* SIDEBAR */}
                <div style={{
                    width: 240,
                    background: "rgba(255,255,255,0.6)",
                    backdropFilter: "blur(10px)",
                    padding: 24,
                    borderRight: "1px solid rgba(0,0,0,0.05)"
                }}>
                    <img
                        src="/logo.png"
                        style={{
                            height: 36,
                            marginBottom: 30,
                            filter: "drop-shadow(0 6px 12px rgba(0,0,0,0.25))"
                        }}
                    />

                    <NavItem label="Dashboard" active={view === "dashboard"} onClick={() => setView("dashboard")} />
                    <NavItem label="Reminders" active={view === "reminders"} onClick={() => setView("reminders")} />
                    <NavItem label="Team" active={view === "team"} onClick={() => setView("team")} />
                    <NavItem label="Settings" active={view === "settings"} onClick={() => setView("settings")} />
                </div>

                {/* MAIN */}
                <div style={{
                    flex: 1,
                    padding: 40
                }}>

                    {view === "dashboard" && (
                        <>
                            {/* TOP BAR */}

                           

                            <div style={{
                                display: "flex",
                                justifyContent: "space-between",
                                alignItems: "center",
                                marginBottom: 40
                            }}>
                                <button
                                    onClick={() => setShowForm(!showForm)}
                                    style={{
                                        background: "linear-gradient(135deg, #3b82f6, #60a5fa)",
                                        color: "white",
                                        padding: "14px 28px",
                                        borderRadius: 999,
                                        border: "none",
                                        fontWeight: 600,
                                        fontSize: 14,
                                        cursor: "pointer",
                                        boxShadow: "0 10px 30px rgba(59,130,246,0.5)",
                                        transition: "0.2s"
                                    }}
                                    onMouseEnter={(e) => {
                                        e.currentTarget.style.transform = "scale(1.05)";
                                    }}
                                    onMouseLeave={(e) => {
                                        e.currentTarget.style.transform = "scale(1)";
                                    }}
                                >
                                    + Add Reminder
                                </button>

                                <div style={{
                                    display: "flex",
                                    alignItems: "center",
                                    gap: 10,
                                    color: "#374151"
                                }}>
                                    👤 {user.email}
                                </div>
                            </div>

                            {showForm && (
                                <div style={{ marginBottom: 30 }}>
                                    <QuickReminder
                                        onAdded={() => {
                                            setShowForm(false);
                                            load();
                                        }}
                                    />
                                </div>
                            )}

                            {/* EXPIRING SOON HEADER */}
                            <div style={{
                                display: "flex",
                                justifyContent: "space-between",
                                alignItems: "center",
                                marginBottom: 16
                            }}>
                                <div style={{
                                    fontSize: 18,
                                    fontWeight: 600,
                                    color: "#111827"
                                }}>
                                    Expiring Soon
                                </div>

                                <div
                                    onClick={() => setView("reminders")}
                                    style={{
                                        fontSize: 13,
                                        color: "#3b82f6",
                                        cursor: "pointer"
                                    }}
                                >
                                    View All →
                                </div>
                            </div>

                            {/* REMINDER CARDS */}
                            <div style={{
                                display: "flex",
                                flexDirection: "column",
                                gap: 16
                            }}>
                                {expiringSoon.map(r => {
                                    const days = Math.ceil(
                                        (new Date(r.due_date) - new Date()) / (1000 * 60 * 60 * 24)
                                    );

                                    return (
                                        <div
                                            key={r.id}
                                            style={{
                                                background: "rgba(255,255,255,0.8)",
                                                backdropFilter: "blur(10px)",
                                                borderRadius: 16,
                                                padding: 20,
                                                border: "1px solid rgba(0,0,0,0.05)",
                                                boxShadow: "0 10px 30px rgba(0,0,0,0.05)",
                                                display: "flex",
                                                justifyContent: "space-between",
                                                alignItems: "center",
                                                transition: "0.2s",
                                                cursor: "pointer"
                                            }}
                                            onMouseEnter={(e) => {
                                                e.currentTarget.style.transform = "translateY(-4px)";
                                                e.currentTarget.style.boxShadow = "0 20px 40px rgba(0,0,0,0.1)";
                                            }}
                                            onMouseLeave={(e) => {
                                                e.currentTarget.style.transform = "translateY(0)";
                                                e.currentTarget.style.boxShadow = "0 10px 30px rgba(0,0,0,0.05)";
                                            }}
                                        >
                                            <div>
                                                <div style={{
                                                    fontWeight: 600,
                                                    fontSize: 16
                                                }}>
                                                    {r.item_title}
                                                </div>

                                                <div style={{
                                                    fontSize: 13,
                                                    color: "#6b7280"
                                                }}>
                                                    Company asset
                                                </div>

                                                <EmailStatus reminder={r} />
                                            </div>

                                            <div style={{
                                                fontWeight: 600,
                                                color: "#3b82f6"
                                            }}>
                                                in {days} days
                                            </div>
                                        </div>
                                    );
                                })}
                            </div>
                        </>
                    )}

                    {/* EXPIRED */}
                    {expired.length > 0 && (
                        <>
                            <div style={{
                                marginTop: 40,
                                marginBottom: 16,
                                fontSize: 18,
                                fontWeight: 600,
                                color: "#111827"
                            }}>
                                Expired
                            </div>

                            <div style={{
                                display: "flex",
                                flexDirection: "column",
                                gap: 16
                            }}>
                                {expired.map(r => (
                                    <div
                                        key={r.id}
                                        style={{
                                            background: "rgba(255,255,255,0.8)",
                                            borderRadius: 16,
                                            padding: 20,
                                            border: "1px solid rgba(0,0,0,0.05)",
                                            display: "flex",
                                            justifyContent: "space-between",
                                            alignItems: "center"
                                        }}
                                    >
                                        <div>
                                            <div style={{ fontWeight: 600 }}>
                                                {r.item_title}
                                            </div>
                                            <div style={{ fontSize: 13, color: "#6b7280" }}>
                                                Expired
                                            </div>
                                        </div>

                                        <div style={{
                                            color: "#ef4444",
                                            fontWeight: 600
                                        }}>
                                            expired
                                        </div>

                                        <EmailStatus reminder={r} />

                                    </div>
                                ))}
                            </div>
                        </>
                    )}

                    {view === "reminders" && (
                        <RemindersTable
                            items={items}
                            remove={remove}
                            edit={edit}
                        />
                    )}

                    {view === "team" && <TeamPanel />}
                    {view === "settings" && <SettingsPanel />}
                </div>
            </div>
        </div>
    );
}
        

/* ---------------- COMPONENTS ---------------- */

function NavItem({ label, active, onClick }) {
    return (
        <div
            onClick={onClick}
            onMouseEnter={(e) => {
                if (!active) e.currentTarget.style.background = "#f1f5f9";
            }}
            onMouseLeave={(e) => {
                if (!active) e.currentTarget.style.background = "transparent";
            }}
            style={{
                padding: "12px 16px",
                borderRadius: 10,
                background: active ? "#eff6ff" : "transparent",
                color: active ? "#2563eb" : "#374151",
                fontWeight: active ? 600 : 500,
                cursor: "pointer",
                transition: "0.2s"
            }}
        >
            {label}
        </div>
    );
}

function SectionTitle({ children }) {
    return (
        <h3 style={{
            marginTop: 20,
            marginBottom: 12,
            fontWeight: 600,
            fontSize: 18,
            color: "#111827"
        }}>
            {children}
        </h3>
    );
}

function Card({ title, subtitle, color }) {
    return (
        <div style={{
            background: "white",
            padding: 20,
            borderRadius: 16,
            width: 260,
            border: "1px solid #e5e7eb",
            boxShadow: "0 4px 20px rgba(0,0,0,0.05)"
        }}>
            <div style={{
                width: 10,
                height: 10,
                borderRadius: "50%",
                background: color,
                marginBottom: 10
            }} />

            <div style={{ fontWeight: 600 }}>{title}</div>
            <div style={{ color: "#6b7280", fontSize: 14 }}>{subtitle}</div>
        </div>
    );
}

function StatusBadge({ status }) {
    let color = "#22c55e";
    let text = "Active";

    if (status === "expired") {
        color = "#ef4444";
        text = "Expired";
    }

    if (status === "urgent") {
        color = "#dc2626";
        text = "URGENT";
    }

    if (status === "soon") {
        color = "#f59e0b";
        text = "Expiring Soon";
    }

    return (
        <span style={{
            background: color,
            color: "white",
            padding: "6px 12px",
            borderRadius: 999,
            fontSize: 12,
            fontWeight: 600
        }}>
            {text}
        </span>
    );
}

function EmailStatus({ reminder }) {
    if (reminder.email_status === "sent") {
        return (
            <div style={{
                fontSize: 12,
                color: "#16a34a",
                marginTop: 6,
                fontWeight: 600
            }}>
                Email sent ✅
            </div>
        );
    }

    return (
        <div style={{
            fontSize: 12,
            color: "#94a3b8",
            marginTop: 6,
            fontWeight: 500
        }}>
            No email sent yet
        </div>
    );
}



function StatCard({ label, value }) {
    return (
        <div style={{
            background: "#f8fafc",
            padding: 20,
            borderRadius: 16,
            border: "1px solid #e5e7eb",
            minWidth: 120,
            boxShadow: "0 4px 10px rgba(0,0,0,0.05)"
        }}>
            <div style={{ fontSize: 12, color: "#6b7280" }}>
                {label}
            </div>
            <div style={{ fontSize: 24, fontWeight: 700 }}>
                {value}
            </div>
        </div>
    );
}

function ReminderCard({ title, subtitle, days, color }) {
    return (
        <div style={{
            flex: "1 1 48%",
            background: "white",
            borderRadius: 14,
            padding: 16,
            border: "1px solid #e5e7eb",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            transition: "0.2s",
            cursor: "pointer"
        }}
            onMouseEnter={(e) => {
                e.currentTarget.style.transform = "translateY(-2px)";
                e.currentTarget.style.boxShadow = "0 8px 20px rgba(0,0,0,0.08)";
            }}
            onMouseLeave={(e) => {
                e.currentTarget.style.transform = "translateY(0)";
                e.currentTarget.style.boxShadow = "none";
            }}
        >
            <div>
                <div style={{ fontWeight: 600 }}>{title}</div>
                <div style={{ fontSize: 13, color: "#6b7280" }}>{subtitle}</div>
            </div>

            <div style={{
                fontSize: 13,
                fontWeight: 600,
                color
            }}>
                {days}
            </div>
        </div>
    );
}


function RemindersTable({ items, remove, edit }) {
    return (
        <>
            <h2 style={{ marginBottom: 20 }}>All Reminders</h2>

            <div style={{
                background: "white",
                borderRadius: 16,
                border: "1px solid #e5e7eb",
                overflow: "hidden"
            }}>
                <table style={{ width: "100%", borderCollapse: "collapse" }}>
                    <thead style={{
                        background: "#f9fafb",
                        fontSize: 12,
                        color: "#6b7280",
                        textTransform: "uppercase"
                    }}>
                        <tr>
                            <th style={thStyle}>Title</th>
                            <th style={thStyle}>Category</th>
                            <th style={thStyle}>Due Date</th>
                            <th style={thStyle}>Status</th>
                            <th style={thStyle}>Email</th>
                            <th style={thStyle}></th>
                        </tr>
                    </thead>

                    <tbody>
                        {items.map((reminder) => {
                            const status = getStatus(reminder.due_date);

                            return (
                                <tr key={reminder.id}>
                                    <td style={tdStyle}>{reminder.item_title}</td>
                                    <td style={tdStyle}>General</td>
                                    <td style={tdStyle}>{formatDate(reminder.due_date)}</td>
                                    <td style={tdStyle}>
                                        <StatusBadge status={status} />
                                    </td>
                                    <td style={tdStyle}>
                                        <EmailStatus reminder={reminder} />
                                    </td>
                                    <td style={tdStyle}>
                                        <button onClick={() => remove(reminder.id)}>❌</button>
                                        <button onClick={() => edit(reminder)}>✏️</button>
                                    </td>
                                </tr>
                            );
                        })}
                    </tbody>
                </table>
            </div>
        </>
    );
}

/* ---------------- STYLES ---------------- */

const thStyle = {
    padding: "12px 16px"
};

const tdStyle = {
    padding: "14px 16px"
};