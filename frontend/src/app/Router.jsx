export default function Router() {
    console.log("🔥 ROUTER RENDERED");
    console.log("PATH:", window.location.pathname);

    const { user, loading } = useAuth();

    console.log("AUTH:", { user, loading });

    if (loading) return <div>Loading...</div>;

    return (
        <BrowserRouter>
            <Routes>
                <Route
                    path="/invite/:token"
                    element={
                        <div>
                            <h1>INVITE ROUTE TEST</h1>
                        </div>
                    }
                />

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