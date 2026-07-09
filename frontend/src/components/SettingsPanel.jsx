import api from "../lib/api";
import { getAuth, signOut } from "firebase/auth";

export default function SettingsPanel() {

    const subscribe = async (plan) => {
        try {
            const res = await api.post("/billing/create-checkout-session", {
                plan: plan
            });

            window.location.href = res.data.checkout_url;

        } catch (e) {
            console.error(e);
            alert("Could not start checkout.");
        }
    };

    const remove = async () => {
        const confirmDelete = confirm("Are you sure? This cannot be undone.");
        if (!confirmDelete) return;

        try {
            await api.delete("/settings/me");

            const auth = getAuth();
            await signOut(auth);

            localStorage.removeItem("token");
            window.location.reload();

        } catch (e) {
            alert("Error deleting account");
            console.error(e);
        }
    };

    const logout = async () => {
        try {
            const auth = getAuth();
            await signOut(auth);

            localStorage.removeItem("token");
            window.location.reload();

        } catch (e) {
            console.error(e);
            alert("Logout failed");
        }
    };

    return (
        <div>
            <h2>Settings</h2>

            <div style={{ marginTop: 24 }}>
                <h3>Subscription</h3>
                <p style={{ color: "#64748b" }}>
                    Choose a plan to activate your company workspace.
                </p>

                <div style={{
                    display: "grid",
                    gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
                    gap: 16,
                    marginTop: 16
                }}>

                    <PlanCard
                        title="Starter"
                        price="29 € / month"
                        items={[
                            "Up to 3 users",
                            "Up to 50 reminders",
                            "Email reminders",
                            "Dashboard"
                        ]}
                        button="Subscribe Starter"
                        onClick={() => subscribe("starter")}
                    />

                    <PlanCard
                        title="Pro"
                        price="59 € / month"
                        items={[
                            "Up to 10 users",
                            "Up to 200 reminders",
                            "Roles & responsibility",
                            "Reports"
                        ]}
                        button="Subscribe Pro"
                        highlighted
                        onClick={() => subscribe("pro")}
                    />

                    <PlanCard
                        title="Business"
                        price="99 € / month"
                        items={[
                            "Unlimited users",
                            "Unlimited reminders",
                            "Full functionality",
                            "Export / API"
                        ]}
                        button="Subscribe Business"
                        onClick={() => subscribe("business")}
                    />

                </div>
            </div>

            <div style={{ marginTop: 32 }}>
                <button
                    onClick={logout}
                    style={{
                        background: "#2563eb",
                        color: "white",
                        padding: "10px 20px",
                        borderRadius: 6,
                        border: "none",
                        marginRight: 10
                    }}
                >
                    Log out
                </button>

                <button
                    onClick={remove}
                    style={{
                        background: "#ef4444",
                        color: "white",
                        padding: "10px 20px",
                        borderRadius: 6,
                        border: "none"
                    }}
                >
                    Delete Account
                </button>
            </div>
        </div>
    );
}


function PlanCard({ title, price, items, button, onClick, highlighted }) {
    return (
        <div style={{
            background: "white",
            borderRadius: 16,
            padding: 22,
            border: highlighted ? "2px solid #2563eb" : "1px solid #e5e7eb",
            boxShadow: highlighted
                ? "0 18px 40px rgba(37, 99, 235, 0.18)"
                : "0 12px 30px rgba(15, 23, 42, 0.08)"
        }}>
            {highlighted && (
                <div style={{
                    color: "#2563eb",
                    fontWeight: 700,
                    fontSize: 13,
                    marginBottom: 8
                }}>
                    Most popular
                </div>
            )}

            <h3 style={{ margin: "0 0 8px" }}>{title}</h3>

            <div style={{
                fontSize: 24,
                fontWeight: 800,
                marginBottom: 16
            }}>
                {price}
            </div>

            <ul style={{
                paddingLeft: 18,
                color: "#475569",
                lineHeight: 1.8,
                minHeight: 120
            }}>
                {items.map((item) => (
                    <li key={item}>{item}</li>
                ))}
            </ul>

            <button
                onClick={onClick}
                style={{
                    width: "100%",
                    background: highlighted ? "#2563eb" : "#0f172a",
                    color: "white",
                    padding: "12px 16px",
                    borderRadius: 10,
                    border: "none",
                    fontWeight: 700,
                    cursor: "pointer"
                }}
            >
                {button}
            </button>
        </div>
    );
}