import { useEffect, useState } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import LoginPage from "./pages/LoginPage";
import AcceptInvitePage from "./pages/AcceptInvitePage";
import { onAuthStateChanged } from "firebase/auth";
import { auth } from "./lib/firebase";
import LandingPage from "./pages/LandingPage";
import IndustryLandingPage from "./pages/IndustryLandingPage";

function App() {
  const [user, setUser] = useState<any>(null);
  const [authChecked, setAuthChecked] = useState(false);

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, async (firebaseUser) => {
      if (!firebaseUser) {
        setUser(null);
        setAuthChecked(true);
        return;
      }

      try {
        const token = await firebaseUser.getIdToken();

        const res = await fetch(`${import.meta.env.VITE_API_URL}/api/auth/me`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        if (!res.ok) {
          console.error("AUTH FAILED:", await res.text());
          setUser(null);
          return;
        }

        const data = await res.json();
        localStorage.setItem("token", token);
        setUser(data);
      } catch (e) {
        console.error("AUTH CHECK ERROR:", e);
        setUser(null);
      } finally {
        setAuthChecked(true);
      }
    });

    return () => unsubscribe();
  }, []);

  if (!authChecked) {
    return <div style={{ padding: 40 }}>Loading...</div>;
  }

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/invite/:token" element={<AcceptInvitePage />} />

        <Route
          path="/"
          element={user ? <Dashboard user={user} /> : <LandingPage />}
        />

        <Route
          path="/construction"
          element={<IndustryLandingPage industry="construction" />}
        />

        <Route
          path="/transport"
          element={<IndustryLandingPage industry="transport" />}
        />

        <Route
          path="/production"
          element={<IndustryLandingPage industry="production" />}
        />

        <Route
          path="/healthcare"
          element={<IndustryLandingPage industry="healthcare" />}
        />

        <Route
          path="/hospitality"
          element={<IndustryLandingPage industry="hospitality" />}
        />

        <Route
          path="/signup"
          element={user ? <Dashboard user={user} /> : <LoginPage onLogin={setUser} />}
        />

        <Route
          path="/login"
          element={user ? <Dashboard user={user} /> : <LoginPage onLogin={setUser} />}
        />

        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;