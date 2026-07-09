import { useNavigate } from "react-router-dom";

const DATA = {
    construction: {
        emoji: "🏗",
        title: "Compliance reminders for construction companies",
        subtitle: "Track safety training, worker medical checks, equipment inspections and fire safety deadlines.",
        bullets: [
            "Health & safety training",
            "Equipment inspections",
            "Worker medical exams",
            "Fire safety checks"
        ]
    },
    transport: {
        emoji: "🚛",
        title: "Compliance reminders for transport companies",
        subtitle: "Track vehicle inspections, driver licenses, medical certificates, insurance and fleet maintenance.",
        bullets: [
            "Vehicle inspections",
            "Driver licenses",
            "Insurance renewals",
            "Fleet maintenance"
        ]
    },
    production: {
        emoji: "🏭",
        title: "Compliance reminders for production companies",
        subtitle: "Track machine inspections, equipment calibration, safety training and ISO certification dates.",
        bullets: [
            "Machine inspections",
            "Equipment calibration",
            "Safety training",
            "ISO reviews"
        ]
    }
};

export default function IndustryLandingPage({ industry }) {
    const navigate = useNavigate();
    const data = DATA[industry];

    return (
        <div style={page}>
            <div style={card}>
                <button onClick={() => navigate("/")} style={backButton}>
                    ← Back
                </button>

                <div style={{ fontSize: 56, marginBottom: 20 }}>{data.emoji}</div>

                <h1 style={title}>{data.title}</h1>

                <p style={subtitle}>{data.subtitle}</p>

                <div style={bulletBox}>
                    {data.bullets.map((b) => (
                        <div key={b} style={bullet}>✓ {b}</div>
                    ))}
                </div>

                <button
                    onClick={() => navigate(`/signup?industry=${industry}`)}
                    style={cta}
                >
                    Start now
                </button>

                <button onClick={() => navigate("/login")} style={loginLink}>
                    Already have an account? Sign in
                </button>
            </div>
        </div>
    );
}

const page = {
    minHeight: "100vh",
    background: "linear-gradient(135deg, #dbeafe, #eff6ff)",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    padding: 24,
    fontFamily: "Inter, sans-serif"
};

const card = {
    width: "100%",
    maxWidth: 840,
    background: "rgba(255,255,255,0.82)",
    borderRadius: 28,
    padding: 56,
    boxShadow: "0 25px 60px rgba(37,99,235,0.18)",
    textAlign: "center",
    position: "relative"
};

const backButton = {
    position: "absolute",
    top: 24,
    left: 24,
    border: "none",
    background: "transparent",
    color: "#2563eb",
    fontWeight: 700,
    cursor: "pointer"
};

const title = {
    fontSize: 42,
    lineHeight: 1.1,
    color: "#0f172a",
    margin: 0,
    marginBottom: 18
};

const subtitle = {
    fontSize: 18,
    lineHeight: 1.6,
    color: "#475569",
    maxWidth: 650,
    margin: "0 auto 34px"
};

const bulletBox = {
    display: "grid",
    gridTemplateColumns: "repeat(2, 1fr)",
    gap: 14,
    marginBottom: 36
};

const bullet = {
    background: "#f8fbff",
    border: "1px solid #dbeafe",
    borderRadius: 16,
    padding: 16,
    color: "#0f172a",
    fontWeight: 700
};

const cta = {
    width: "100%",
    maxWidth: 360,
    padding: "16px 20px",
    borderRadius: 999,
    border: "none",
    background: "linear-gradient(135deg, #3b82f6, #60a5fa)",
    color: "white",
    fontWeight: 800,
    fontSize: 17,
    cursor: "pointer",
    boxShadow: "0 12px 30px rgba(59,130,246,0.4)"
};

const loginLink = {
    display: "block",
    margin: "24px auto 0",
    border: "none",
    background: "transparent",
    color: "#2563eb",
    fontWeight: 700,
    cursor: "pointer"
};