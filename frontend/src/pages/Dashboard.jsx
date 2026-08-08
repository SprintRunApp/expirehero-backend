import { useEffect, useState } from "react";
import api from "../lib/api";
import QuickReminder from "../components/QuickReminder";
import TeamPanel from "../components/TeamPanel";
import SettingsPanel from "../components/SettingsPanel";

/* ---------------- HELPERS ---------------- */



function formatDate(date) {
    return new Date(date).toLocaleDateString();
}

/* ---------------- MAIN ---------------- */

export default function Dashboard({ user }) {
    const [items, setItems] = useState([]);
    const [showForm, setShowForm] = useState(false);
    const [view, setView] = useState("dashboard");
    const [team, setTeam] = useState(null);

    const [notificationModal, setNotificationModal] = useState(null);
    const [notificationHistory, setNotificationHistory] = useState([]);

    const [workflows, setWorkflows] = useState([]);
    const [workflowStatus, setWorkflowStatus] = useState("active");

    const [completionModal, setCompletionModal] = useState(null);
    const [completionHistory, setCompletionHistory] = useState([]);

    const load = async () => {
        const res = await api.get("/reminders/");
        setItems(res.data);
    };

    const openNotificationHistory = async (reminder) => {
        try {
            const res = await api.get(
                `/reminders/${reminder.id}/notifications`
            );

            setNotificationHistory(res.data);
            setNotificationModal(reminder);

        } catch (e) {
            alert("Cannot load notification history");
        }
    };

    const loadTeam = async () => {
        try {
            const res = await api.get("/teams/me");
            setTeam(res.data);
        } catch (e) {
            setTeam(null);
        }
    };

    useEffect(() => {
        load();
        loadTeam();
    }, []);

    const loadWorkflows = async (status = workflowStatus) => {
        try {
            const res = await api.get(
                `/items/?workflow_status=${status}`
            );

            setWorkflows(res.data);

        } catch (e) {
            console.error(
                "LOAD WORKFLOWS ERROR:",
                e
            );

            alert("Cannot load workflows");
        }
    };

    useEffect(() => {
        if (view === "workflows") {
            loadWorkflows(workflowStatus);
        }
    }, [view, workflowStatus]);

    const openCompletionHistory = async (workflow) => {
        try {
            const res = await api.get(
                `/items/${workflow.id}/completions`
            );

            setCompletionHistory(res.data);
            setCompletionModal(workflow);

        } catch (e) {
            console.error(
                "COMPLETION HISTORY ERROR:",
                e
            );

            alert(
                "Cannot load completion history"
            );
        }
    };

    const completeItem = async (workflow) => {
        const notes = prompt(
            "Optional completion note:",
            ""
        );

        try {
            await api.post(
                `/items/${workflow.id}/complete`,
                {
                    notes: notes || null,
                }
            );

            await loadWorkflows(workflowStatus);
            await load();

        } catch (e) {
            console.error(
                "COMPLETE WORKFLOW ERROR:",
                e
            );

            alert(
                e.response?.data?.detail ||
                "Could not complete workflow."
            );
        }
    };


    const cancelItem = async (workflow) => {
        if (
            !confirm(
                `Cancel "${workflow.title}"?`
            )
        ) {
            return;
        }

        try {
            await api.post(
                `/items/${workflow.id}/cancel`
            );

            await loadWorkflows(workflowStatus);
            await load();

        } catch (e) {
            console.error(
                "CANCEL WORKFLOW ERROR:",
                e
            );

            alert(
                e.response?.data?.detail ||
                "Could not cancel workflow."
            );
        }
    };


    const reopenItem = async (workflow) => {
        try {
            await api.post(
                `/items/${workflow.id}/reopen`
            );

            await loadWorkflows(workflowStatus);
            await load();

        } catch (e) {
            console.error(
                "REOPEN WORKFLOW ERROR:",
                e
            );

            alert(
                e.response?.data?.detail ||
                "Could not reopen workflow."
            );
        }
    };

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

    const completeWorkflow = async (reminder) => {
        try {
            const notes = prompt(
                "Optional completion note:",
                ""
            );

            await api.post(
                `/items/${reminder.item_id}/complete`,
                {
                    notes: notes || null,
                }
            );

            await load();

        } catch (e) {
            console.error(
                "COMPLETE WORKFLOW ERROR:",
                e
            );

            alert(
                e.response?.data?.detail ||
                "Could not complete workflow."
            );
        }
    };


    const cancelWorkflow = async (reminder) => {
        if (
            !confirm(
                `Cancel "${reminder.item_title}"?`
            )
        ) {
            return;
        }

        try {
            await api.post(
                `/items/${reminder.item_id}/cancel`
            );

            await load();

        } catch (e) {
            console.error(
                "CANCEL WORKFLOW ERROR:",
                e
            );

            alert(
                e.response?.data?.detail ||
                "Could not cancel workflow."
            );
        }
    };

    const expiringSoon = items.filter((r) => {
        return (
            r.ui_status === "soon" ||
            r.ui_status === "urgent"
        );
    });

    const expired = items.filter((r) => {
        return r.ui_status === "expired";
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
                    <NavItem
                        label="Workflows"
                        active={view === "workflows"}
                        onClick={() => setView("workflows")}
                    />
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
                               {team ? (
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
                                ) : (
                                    <div style={{
                                        background: "#eef2ff",
                                        color: "#475569",
                                        padding: "12px 16px",
                                        borderRadius: 999,
                                        fontSize: 14,
                                        fontWeight: 600
                                    }}>
                                        You are not assigned to a company
                                    </div>
                                )}

                                <div style={{
                                    display: "flex",
                                    alignItems: "center",
                                    gap: 10,
                                    color: "#374151"
                                }}>
                                    👤 {user.email}
                                </div>
                            </div>

                            {showForm && team && (
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

                                                
                                            </div>

                                            <EmailStatus
                                                reminder={r}
                                                onClick={() => openNotificationHistory(r)}
                                            />

                                            <div style={{
                                                fontWeight: 600,
                                                color: "#3b82f6"
                                            }}>
                                                in {r.days_left} days
                                            </div>
                                        </div>
                                    );
                                })}
                            </div>
                        </>
                    )}

                    {/* EXPIRED */}
                    {view === "dashboard" && expired.length > 0 && (
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

                                        <EmailStatus
                                            reminder={r}
                                            onClick={() => openNotificationHistory(r)}
                                        />

                                        <div style={{
                                            color: "#ef4444",
                                            fontWeight: 600
                                        }}>
                                            expired
                                        </div>

                                        

                                    </div>
                                ))}
                            </div>
                        </>
                    )}

                    {view === "workflows" && (
                        <>
                            <div
                                style={{
                                    display: "flex",
                                    justifyContent: "space-between",
                                    alignItems: "center",
                                    marginBottom: 24,
                                }}
                            >
                                <div>
                                    <h2
                                        style={{
                                            margin: 0,
                                            color: "#0f172a",
                                        }}
                                    >
                                        Workflows
                                    </h2>

                                    <div
                                        style={{
                                            marginTop: 6,
                                            color: "#64748b",
                                            fontSize: 14,
                                        }}
                                    >
                                        Manage the lifecycle of your
                                        company obligations.
                                    </div>
                                </div>
                            </div>

                            <WorkflowTabs
                                status={workflowStatus}
                                onChange={setWorkflowStatus}
                            />

                            <WorkflowsTable
                                workflows={workflows}
                                completeItem={completeItem}
                                cancelItem={cancelItem}
                                reopenItem={reopenItem}
                                openCompletionHistory={
                                    openCompletionHistory
                                }
                            />
                        </>
                    )}

                    {view === "reminders" && (
                        <RemindersTable
                            items={items}
                            remove={remove}
                            edit={edit}
                            completeWorkflow={completeWorkflow}
                            cancelWorkflow={cancelWorkflow}
                            openNotificationHistory={openNotificationHistory}
                        />
                    )}

                    {view === "team" && <TeamPanel />}
                    {view === "settings" && <SettingsPanel />}

                    {notificationModal && (
                        <div style={{
                            position: "fixed",
                            inset: 0,
                            background: "rgba(0,0,0,0.45)",
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                            zIndex: 9999
                        }}>
                            <div style={{
                                width: 700,
                                maxHeight: "80vh",
                                overflowY: "auto",
                                background: "white",
                                borderRadius: 20,
                                padding: 24,
                                boxShadow: "0 30px 80px rgba(0,0,0,0.3)"
                            }}>

                                <div style={{
                                    display: "flex",
                                    justifyContent: "space-between",
                                    alignItems: "center",
                                    marginBottom: 20
                                }}>
                                    <h2>
                                        Email History
                                    </h2>

                                    <button
                                        onClick={() => setNotificationModal(null)}
                                    >
                                        ✖
                                    </button>
                                </div>

                                {notificationHistory.length === 0 && (
                                    <div>
                                        No emails yet
                                    </div>
                                )}

                                {notificationHistory.map((n) => (
                                    <div
                                        key={n.id}
                                        style={{
                                            padding: 16,
                                            border: "1px solid #e5e7eb",
                                            borderRadius: 12,
                                            marginBottom: 12
                                        }}
                                    >
                                        <div>
                                            <strong>Recipient:</strong> {n.recipient_email}
                                        </div>

                                        <div>
                                            <strong>Status:</strong> {n.status}
                                        </div>

                                        <div>
                                            <strong>Trigger:</strong> {n.trigger_days} days
                                        </div>

                                        <div>
                                            <strong>Sent:</strong>{" "}
                                            {n.sent_at
                                                ? new Date(n.sent_at).toLocaleString()
                                                : "Not sent"}
                                        </div>

                                        {n.error && (
                                            <div style={{
                                                color: "#dc2626",
                                                marginTop: 8
                                            }}>
                                                {n.error}
                                            </div>
                                        )}
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}


                    {completionModal && (
                        <div
                            style={{
                                position: "fixed",
                                inset: 0,
                                background: "rgba(0,0,0,0.45)",
                                display: "flex",
                                alignItems: "center",
                                justifyContent: "center",
                                zIndex: 9999,
                            }}
                        >
                            <div
                                style={{
                                    width: 700,
                                    maxHeight: "80vh",
                                    overflowY: "auto",
                                    background: "white",
                                    borderRadius: 20,
                                    padding: 24,
                                    boxShadow: "0 30px 80px rgba(0,0,0,0.3)",
                                }}
                            >
                                <div
                                    style={{
                                        display: "flex",
                                        justifyContent: "space-between",
                                        alignItems: "center",
                                        marginBottom: 20,
                                    }}
                                >
                                    <div>
                                        <h2
                                            style={{
                                                margin: 0,
                                            }}
                                        >
                                            Completion History
                                        </h2>

                                        <div
                                            style={{
                                                marginTop: 4,
                                                color: "#64748b",
                                            }}
                                        >
                                            {completionModal.title}
                                        </div>
                                    </div>

                                    <button
                                        onClick={() =>
                                            setCompletionModal(null)
                                        }
                                    >
                                        ✖
                                    </button>
                                </div>

                                {completionHistory.length === 0 && (
                                    <div
                                        style={{
                                            color: "#64748b",
                                        }}
                                    >
                                        No completion history yet.
                                    </div>
                                )}

                                {completionHistory.map((entry) => (
                                    <div
                                        key={entry.id}
                                        style={{
                                            padding: 16,
                                            border: "1px solid #e5e7eb",
                                            borderRadius: 12,
                                            marginBottom: 12,
                                        }}
                                    >
                                        <div>
                                            <strong>Completed by:</strong>{" "}
                                            {entry.completed_by_name ||
                                                entry.completed_by_email ||
                                                "Unknown"}
                                        </div>

                                        <div>
                                            <strong>Completed:</strong>{" "}
                                            {new Date(
                                                entry.completed_at
                                            ).toLocaleString()}
                                        </div>

                                        <div>
                                            <strong>Previous due date:</strong>{" "}
                                            {entry.previous_due_date
                                                ? formatDate(
                                                    entry.previous_due_date
                                                )
                                                : "—"}
                                        </div>

                                        <div>
                                            <strong>Next due date:</strong>{" "}
                                            {entry.next_due_date
                                                ? formatDate(
                                                    entry.next_due_date
                                                )
                                                : "—"}
                                        </div>

                                        {entry.notes && (
                                            <div
                                                style={{
                                                    marginTop: 10,
                                                    padding: 10,
                                                    background: "#f8fafc",
                                                    borderRadius: 8,
                                                }}
                                            >
                                                <strong>Notes:</strong>{" "}
                                                {entry.notes}
                                            </div>
                                        )}
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

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

function EmailStatus({ reminder, onClick }) {
    if (reminder.email_status === "sent") {
        return (
            <div
                onClick={onClick}
                style={{
                    fontSize: 12,
                    color: "#16a34a",
                    marginTop: 6,
                    fontWeight: 600,
                    cursor: "pointer"
                }}
            >
                Email sent ✅
            </div>
        );
    }

    return (
        <div
            onClick={onClick}
            style={{
                fontSize: 12,
                color: "#94a3b8",
                marginTop: 6,
                fontWeight: 500,
                cursor: "pointer"
            }}
        >
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

function WorkflowTabs({
    status,
    onChange,
}) {
    const tabs = [
        {
            id: "active",
            label: "Active",
        },
        {
            id: "completed",
            label: "Completed",
        },
        {
            id: "cancelled",
            label: "Cancelled",
        },
    ];

    return (
        <div
            style={{
                display: "flex",
                gap: 8,
                marginBottom: 20,
            }}
        >
            {tabs.map((tab) => {
                const active =
                    status === tab.id;

                return (
                    <button
                        key={tab.id}
                        onClick={() =>
                            onChange(tab.id)
                        }
                        style={{
                            border: active
                                ? "1px solid #3b82f6"
                                : "1px solid #e2e8f0",
                            background: active
                                ? "#eff6ff"
                                : "white",
                            color: active
                                ? "#2563eb"
                                : "#64748b",
                            padding: "10px 18px",
                            borderRadius: 999,
                            fontWeight: 700,
                            cursor: "pointer",
                        }}
                    >
                        {tab.label}
                    </button>
                );
            })}
        </div>
    );
}

function WorkflowsTable({
    workflows,
    completeItem,
    cancelItem,
    reopenItem,
    openCompletionHistory,
}) {
    if (workflows.length === 0) {
        return (
            <div
                style={{
                    background: "white",
                    borderRadius: 16,
                    padding: 30,
                    color: "#64748b",
                    textAlign: "center",
                    border: "1px solid #e5e7eb",
                }}
            >
                No workflows in this section.
            </div>
        );
    }

    return (
        <div
            style={{
                background: "white",
                borderRadius: 16,
                border: "1px solid #e5e7eb",
                overflow: "hidden",
            }}
        >
            <table
                style={{
                    width: "100%",
                    borderCollapse: "collapse",
                }}
            >
                <thead
                    style={{
                        background: "#f9fafb",
                        fontSize: 12,
                        color: "#6b7280",
                        textTransform: "uppercase",
                    }}
                >
                    <tr>
                        <th style={thStyle}>
                            Workflow
                        </th>

                        <th style={thStyle}>
                            Category
                        </th>

                        <th style={thStyle}>
                            Status
                        </th>

                        <th style={thStyle}>
                            Completed
                        </th>

                        <th style={thStyle}>
                            Actions
                        </th>
                    </tr>
                </thead>

                <tbody>
                    {workflows.map(
                        (workflow) => (
                            <tr key={workflow.id}>
                                <td style={tdStyle}>
                                    <strong>
                                        {
                                            workflow.title
                                        }
                                    </strong>
                                </td>

                                <td style={tdStyle}>
                                    {
                                        workflow.category
                                    }
                                </td>

                                <td style={tdStyle}>
                                    <WorkflowStatusBadge
                                        status={
                                            workflow.status
                                        }
                                    />
                                </td>

                                <td style={tdStyle}>
                                    {workflow.completed_at
                                        ? new Date(
                                            workflow.completed_at
                                        ).toLocaleString()
                                        : "—"}
                                </td>

                                <td style={tdStyle}>
                                    <div
                                        style={{
                                            display:
                                                "flex",
                                            gap: 6,
                                            flexWrap:
                                                "wrap",
                                        }}
                                    >
                                        {workflow.status ===
                                            "active" && (
                                                <>
                                                    <button
                                                        onClick={() =>
                                                            completeItem(
                                                                workflow
                                                            )
                                                        }
                                                        title="Complete"
                                                    >
                                                        ✅
                                                    </button>

                                                    <button
                                                        onClick={() =>
                                                            cancelItem(
                                                                workflow
                                                            )
                                                        }
                                                        title="Cancel"
                                                    >
                                                        ⛔
                                                    </button>
                                                </>
                                            )}

                                        {(workflow.status ===
                                            "completed" ||
                                            workflow.status ===
                                            "cancelled") && (
                                                <button
                                                    onClick={() =>
                                                        reopenItem(
                                                            workflow
                                                        )
                                                    }
                                                    title="Reopen"
                                                >
                                                    ↻
                                                </button>
                                            )}

                                        <button
                                            onClick={() =>
                                                openCompletionHistory(
                                                    workflow
                                                )
                                            }
                                            title="Completion history"
                                        >
                                            📜
                                        </button>
                                    </div>
                                </td>
                            </tr>
                        )
                    )}
                </tbody>
            </table>
        </div>
    );
}

function WorkflowStatusBadge({ status }) {
    let background = "#dcfce7";
    let color = "#166534";
    let text = "Active";

    if (status === "completed") {
        background = "#dbeafe";
        color = "#1d4ed8";
        text = "Completed";
    }

    if (status === "cancelled") {
        background = "#f1f5f9";
        color = "#64748b";
        text = "Cancelled";
    }

    return (
        <span
            style={{
                background,
                color,
                padding: "6px 10px",
                borderRadius: 999,
                fontSize: 12,
                fontWeight: 700,
            }}
        >
            {text}
        </span>
    );
}


function RemindersTable({
    items,
    remove,
    edit,
    completeWorkflow,
    cancelWorkflow,
    openNotificationHistory
}) {
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
                            return (
                                <tr key={reminder.id}>
                                    <td style={tdStyle}>{reminder.item_title}</td>
                                    <td style={tdStyle}>General</td>
                                    <td style={tdStyle}>{formatDate(reminder.due_date)}</td>
                                    <td style={tdStyle}>
                                        <StatusBadge status={reminder.ui_status} />
                                    </td>
                                    <td style={tdStyle}>
                                        <EmailStatus
                                            reminder={reminder}
                                            onClick={() => openNotificationHistory(reminder)}
                                        />
                                    </td>
                                    <td style={tdStyle}>
                                        <button
                                            onClick={() =>
                                                completeWorkflow(reminder)
                                            }
                                            title="Complete workflow"
                                        >
                                            ✅
                                        </button>

                                        <button
                                            onClick={() =>
                                                cancelWorkflow(reminder)
                                            }
                                            title="Cancel workflow"
                                        >
                                            ⛔
                                        </button>

                                        <button
                                            onClick={() =>
                                                edit(reminder)
                                            }
                                            title="Edit due date"
                                        >
                                            ✏️
                                        </button>

                                        <button
                                            onClick={() =>
                                                remove(reminder.id)
                                            }
                                            title="Delete reminder"
                                        >
                                            ❌
                                        </button>
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