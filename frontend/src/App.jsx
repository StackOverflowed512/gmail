// import from node
import { BrowserRouter, Routes, Route } from "react-router";

//user defined import
import Intro from "./pages/Intro";
import Inbox from "./pages/Inbox";
import Login from "./pages/Login";
import NotFound from "./pages/NotFound";
import { AuthProvider } from "./context/AuthContext";
import RequireAuth from "./context/RequireAuth";
import DashboardLayout from "./pages/DashboardLayout";
import Dashboard from "./pages/Dashboard";
import ResponseMail from "./pages/ResponseMail";
import SentBox from "./pages/SentBox";
import MailViewer from "./pages/MailViewer";
import Footer from "./components/Footer";
import { HistoryProvider } from "./context/HistoryContext";
import Settings from "./pages/Settings";

function App() {
    return (
        <div className="max-w-screen flex flex-col min-h-screen">
            <AuthProvider>
                <HistoryProvider>
                    <BrowserRouter>
                        <Routes>
                            <Route path="/" element={<Login />} />
                            <Route
                                path="/dashboard"
                                element={
                                    <RequireAuth>
                                        <DashboardLayout />
                                    </RequireAuth>
                                }
                            >
                                <Route
                                    path="home"
                                    element={
                                        <RequireAuth>
                                            <Dashboard />
                                        </RequireAuth>
                                    }
                                />
                                <Route
                                    path="inbox"
                                    element={
                                        <RequireAuth>
                                            <Inbox />
                                        </RequireAuth>
                                    }
                                />
                                <Route
                                    path="inbox/:uid"
                                    element={
                                        <RequireAuth>
                                            <ResponseMail />
                                        </RequireAuth>
                                    }
                                />
                                <Route
                                    path="sent"
                                    element={
                                        <RequireAuth>
                                            <SentBox />
                                        </RequireAuth>
                                    }
                                />
                                <Route
                                    path="sent/:uid"
                                    element={
                                        <RequireAuth>
                                            <MailViewer />
                                        </RequireAuth>
                                    }
                                />
                                <Route
                                    path="settings"
                                    element={
                                        <RequireAuth>
                                            <Settings />
                                        </RequireAuth>
                                    }
                                />
                            </Route>
                            {/* Add 404 route */}
                            <Route path="*" element={<NotFound />} />
                        </Routes>
                    </BrowserRouter>
                </HistoryProvider>
            </AuthProvider>
        </div>
    );
}

export default App;
