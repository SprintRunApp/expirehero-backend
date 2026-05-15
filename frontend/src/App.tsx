import { useEffect, useState } from "react";
import Dashboard from "./pages/Dashboard";
import LoginPage from "./pages/LoginPage";
import { onAuthStateChanged } from "firebase/auth";
import { auth } from "./lib/firebase";

function App() {
  const [user, setUser] = useState<any>(null);

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, async (firebaseUser) => {
      if (!firebaseUser) {
        setUser(null);
        return;
      }

      // 🔥 ZAWSZE świeży token
      const token = await firebaseUser.getIdToken();

      console.log("FRESH TOKEN:", token);

      const res = await fetch(`${import.meta.env.VITE_API_URL}/api/auth/me`, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });

      if (!res.ok) {
        console.error("AUTH FAILED:", await res.text());
        setUser(null);
        return;
      }

      const data = await res.json();
      setUser(data);

      localStorage.setItem("token", token); // optional

      setUser(data);
    });

    return () => unsubscribe();
  }, []);

  if (!user) {
    console.log("NO USER");
    return <LoginPage onLogin={setUser} />;
  }

  console.log("USER LOGGED:", user);

  return <Dashboard user={user} />;
}

export default App;