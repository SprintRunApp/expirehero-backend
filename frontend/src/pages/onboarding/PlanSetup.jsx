import { useNavigate, useSearchParams } from "react-router-dom";
import api from "../../lib/api";

export default function PlanSetup() {
    const navigate = useNavigate();
    const [searchParams] = useSearchParams();

    const industry = searchParams.get("industry");

    const subscribe = async (plan) => {
        try {
            const res = await api.post(
                "/billing/create-checkout-session",
                {
                    plan,
                    success_path:
                        `/setup/templates?industry=${industry}`,
                    cancel_path:
                        `/setup/plan?industry=${industry}`,
                }
            );

            window.location.href =
                res.data.checkout_url;

        } catch (e) {
            console.error(e);
            alert("Could not start checkout.");
        }
    };

    return (
        <div style={page}>
            <div style={container}>
                <div style={header}>
                    <h1 style={title}>
                        Choose your plan
                    </h1>

                    <p style={subtitle}>
                        Activate your ExpireHeros workspace.
                    </p>
                </div>

                <div style={grid}>
                    <PlanCard
                        title="Starter"
                        price="€29 / month"
                        items={[
                            "Up to 3 users",
                            "Up to 50 reminders",
                            "Email protection alerts",
                            "Dashboard",
                        ]}
                        button="Choose Starter"
                        onClick={() =>
                            subscribe("starter")
                        }
                    />

                    <PlanCard
                        title="Pro"
                        price="€59 / month"
                        items={[
                            "Up to 10 users",
                            "Up to 200 reminders",
                            "Roles & responsibility",
                            "Workflow groups",
                            "Protection Engine",
                        ]}
                        button="Choose Pro"
                        highlighted
                        onClick={() =>
                            subscribe("pro")
                        }
                    />

                    <PlanCard
                        title="Business"
                        price="€99 / month"
                        items={[
                            "Unlimited users",
                            "Unlimited reminders",
                            "Full functionality",
                            "External actions",
                            "Export / API",
                        ]}
                        button="Choose Business"
                        onClick={() =>
                            subscribe("business")
                        }
                    />
                </div>

                <button
                    onClick={() =>
                        navigate("/")
                    }
                    style={backButton}
                >
                    Cancel
                </button>
            </div>
        </div>
    );
}


function PlanCard({
    title,
    price,
    items,
    button,
    onClick,
    highlighted,
}) {
    return (
        <div
            style={{
                ...card,
                ...(highlighted
                    ? highlightedCard
                    : {}),
            }}
        >
            {highlighted && (
                <div style={popular}>
                    Most popular
                </div>
            )}

            <h2 style={cardTitle}>
                {title}
            </h2>

            <div style={priceStyle}>
                {price}
            </div>

            <ul style={features}>
                {items.map((item) => (
                    <li key={item}>
                        {item}
                    </li>
                ))}
            </ul>

            <button
                onClick={onClick}
                style={{
                    ...chooseButton,
                    ...(highlighted
                        ? highlightedButton
                        : {}),
                }}
            >
                {button}
            </button>
        </div>
    );
}


const page = {
    minHeight: "100vh",
    background:
        "linear-gradient(135deg, #dbeafe, #eff6ff)",
    padding: "60px 20px",
    fontFamily: "Inter, sans-serif",
};

const container = {
    maxWidth: 1100,
    margin: "0 auto",
};

const header = {
    textAlign: "center",
    marginBottom: 36,
};

const title = {
    fontSize: 38,
    margin: 0,
    color: "#0f172a",
};

const subtitle = {
    marginTop: 10,
    color: "#64748b",
    fontSize: 17,
};

const grid = {
    display: "grid",
    gridTemplateColumns:
        "repeat(auto-fit, minmax(260px, 1fr))",
    gap: 20,
};

const card = {
    background: "white",
    borderRadius: 20,
    padding: 26,
    border: "1px solid #e5e7eb",
    boxShadow:
        "0 12px 30px rgba(15, 23, 42, 0.08)",
};

const highlightedCard = {
    border: "2px solid #2563eb",
    boxShadow:
        "0 18px 40px rgba(37,99,235,0.18)",
};

const popular = {
    color: "#2563eb",
    fontWeight: 800,
    fontSize: 13,
    marginBottom: 10,
};

const cardTitle = {
    margin: "0 0 8px",
};

const priceStyle = {
    fontSize: 28,
    fontWeight: 800,
    marginBottom: 18,
};

const features = {
    paddingLeft: 20,
    color: "#475569",
    lineHeight: 1.9,
    minHeight: 150,
};

const chooseButton = {
    width: "100%",
    padding: "13px 16px",
    borderRadius: 12,
    border: "none",
    background: "#0f172a",
    color: "white",
    fontWeight: 800,
    cursor: "pointer",
};

const highlightedButton = {
    background: "#2563eb",
};

const backButton = {
    display: "block",
    margin: "28px auto 0",
    border: "none",
    background: "transparent",
    color: "#64748b",
    fontWeight: 700,
    cursor: "pointer",
};