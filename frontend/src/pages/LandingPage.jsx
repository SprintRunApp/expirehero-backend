import { useNavigate } from "react-router-dom";

export default function LandingPage() {
    const navigate = useNavigate();

    return (
        <div style={page}>
            <div style={card}>
                <img src="/logo.png" style={{ height: 52, marginBottom: 40 }} />

                <h1 style={title}>
                    Never miss a certificate, inspection or important deadline.
                </h1>

                <p style={subtitle}>
                    ExpireHeros helps companies track compliance deadlines, inspections,
                    certificates and renewals in one simple dashboard.
                </p>

                <h2 style={sectionTitle}>Choose your industry</h2>

                <div style={grid}>
                    <IndustryButton emoji="🏗" title="Construction" onClick={() => navigate("/construction")} />
                    <IndustryButton emoji="🚛" title="Transport" onClick={() => navigate("/transport")} />
                    <IndustryButton emoji="🏭" title="Production" onClick={() => navigate("/production")} />
                </div>

                <button onClick={() => navigate("/login")} style={loginLink}>
                    Already have an account? Sign in
                </button>
            </div>
        </div>
    );
}

function IndustryButton({ emoji, title, onClick }) {
    return (
        <button onClick={onClick} style={industryButton}>
            <div style={{ fontSize: 34 }}>{emoji}</div>
            <div style={{ fontWeight: 800, fontSize: 18 }}>{title}</div>
        </button>
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
    maxWidth: 960,
    background: "rgba(255,255,255,0.78)",
    borderRadius: 28,
    padding: 56,
    boxShadow: "0 25px 60px rgba(37,99,235,0.18)",
    textAlign: "center"
};

const title = {
    fontSize: 46,
    lineHeight: 1.1,
    color: "#0f172a",
    margin: 0,
    marginBottom: 20
};

const subtitle = {
    fontSize: 18,
    lineHeight: 1.6,
    color: "#475569",
    maxWidth: 720,
    margin: "0 auto 44px"
};

const sectionTitle = {
    fontSize: 22,
    color: "#0f172a",
    marginBottom: 20
};

const grid = {
    display: "grid",
    gridTemplateColumns: "repeat(3, 1fr)",
    gap: 18
};

const industryButton = {
    border: "1px solid #dbeafe",
    background: "white",
    borderRadius: 22,
    padding: 28,
    cursor: "pointer",
    color: "#0f172a",
    boxShadow: "0 12px 28px rgba(37,99,235,0.12)"
};

const loginLink = {
    marginTop: 34,
    border: "none",
    background: "transparent",
    color: "#2563eb",
    fontWeight: 700,
    cursor: "pointer"
};