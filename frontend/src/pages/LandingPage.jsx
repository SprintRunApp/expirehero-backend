import { useNavigate } from "react-router-dom";
import { INDUSTRIES } from "../data/industries";
import "../App.css";

export default function LandingPage() {
    const navigate = useNavigate();

    return (
        <div className="landing-page">
            <div className="landing-card">
                <img
                    src="/logo.png"
                    alt="ExpireHeros"
                    className="landing-logo"
                />

                <h1 className="landing-title">
                    Never miss a certificate, inspection or important deadline.
                </h1>

                <p className="landing-subtitle">
                    ExpireHeros helps companies track compliance deadlines,
                    inspections, certificates and renewals in one simple dashboard.
                </p>

                <h2 className="landing-section-title">
                    Choose your industry
                </h2>

                <div className="industry-grid">
                    {INDUSTRIES.map((industry) => (
                        <IndustryButton
                            key={industry.id}
                            emoji={industry.emoji}
                            title={industry.name}
                            onClick={() => navigate(`/${industry.id}`)}
                        />
                    ))}
                </div>

                <button
                    onClick={() => navigate("/login")}
                    className="landing-login-link"
                >
                    Already have an account? Sign in
                </button>
            </div>
        </div>
    );
}

function IndustryButton({ emoji, title, onClick }) {
    return (
        <button
            onClick={onClick}
            className="industry-button"
        >
            <div className="industry-emoji">
                {emoji}
            </div>

            <div className="industry-name">
                {title}
            </div>
        </button>
    );
}