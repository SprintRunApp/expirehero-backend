import api from "../lib/api";
import { getAuth, signOut } from "firebase/auth";

export default function SettingsPanel() {

    const remove = async () => {
        const confirmDelete = confirm("Are you sure? This cannot be undone.");

        if (!confirmDelete) return;

        try {
            await api.delete("/settings/me");

            // 🔥 logout
            const auth = getAuth();
            await signOut(auth);

            localStorage.removeItem("token");

            window.location.reload();

        } catch (e) {
            alert("Error deleting account");
            console.error(e);
        }
    };

    return (
        <div>
            <h2>Settings</h2>

            <div style={{ marginTop: 20 }}>
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