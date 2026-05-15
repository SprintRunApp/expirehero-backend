import { useState } from "react";
import api from "../lib/api";

export default function QuickReminder({ onAdded }) {
    const [title, setTitle] = useState("");
    const [date, setDate] = useState("");
    const [loading, setLoading] = useState(false);
    const [visibility, setVisibility] = useState("private");

    const save = async () => {
        if (!title || !date) return;

        try {
            setLoading(true);

            const item = await api.post("/items/", {
                title,
                category: "General",
                visibility: visibility
            });

            await api.post("/reminders/", {
                item_id: item.data.id,
                due_date: date,
            });

            setTitle("");
            setDate("");
            setVisibility("private");
            onAdded();

        } catch (e) {
            console.error("🔥 ERROR:", e);
            console.error("🔥 RESPONSE:", e.response);

            alert(e.response?.data?.detail || "Error saving reminder");
        
        
        } finally {
            setLoading(false);
        }
    };

    return (
        <div style={{
            display: "flex",
            gap: 10,
            marginBottom: 20
        }}>
            <input
                placeholder="What expires?"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                style={{ padding: 10, flex: 1 }}
            />

            <input
                type="date"
                value={date}
                onChange={(e) => setDate(e.target.value)}
                style={{ padding: 10 }}
            />

            <select
                value={visibility}
                onChange={(e) => setVisibility(e.target.value)}
                style={{ padding: 10 }}
            >
                <option value="private">Private</option>
                <option value="team">Team</option>
            </select>

            <button
                onClick={save}
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
    );
}