import { BrowserRouter, Routes, Route } from "react-router-dom";

import Login from "../pages/Login";
import Dashboard from "../pages/Dashboard";
import Items from "../pages/Items";

import useAuth from "../hooks/useAuth";

import AcceptInvitePage from "../pages/AcceptInvitePage";

export default function Router() {

    const { user, loading } = useAuth();

    if (loading) return <div>Loading...</div>;

    return (
        <BrowserRouter>
            <Routes>
                
                <Route path="/invite/:token" element={<AcceptInvitePage />} />

                {!user && (
                    <Route path="*" element={<Login />} />
                )}

                {user && (
                    <>
                        <Route path="/" element={<Dashboard user={user} />} />
                        <Route path="/items" element={<Items />} />
                    </>
                )}

            </Routes>
        </BrowserRouter>
    );
}