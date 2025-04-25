import { Info, X } from "lucide-react";
import { useState, useEffect } from "react";
import { useNavigate } from "react-router";
import { useAuth } from "../context/AuthContext";
import Footer from "../components/Footer";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [showAccounts, setShowAccounts] = useState(false);
  const navigate = useNavigate();
  const { login } = useAuth();
  const [savedAccounts, setSavedAccounts] = useState(() => {
    const accounts = localStorage.getItem("savedAccounts");
    return accounts ? JSON.parse(accounts) : [];
  });

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const token = localStorage.getItem("access_token");
        if (token) {
          const response = await fetch("/api/protected", {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          });
          if (response.ok) {
            navigate("/dashboard");
          }
        }
      } catch (err) {
        console.error("Auth check failed:", err);
      }
    };
    checkAuth();
  }, [navigate]);

  const handleLogin = async (e) => {
    setLoading(true);
    e.preventDefault();
    setError("");
    try {
      const result = await login(email, password);
      if (result.success) {
        const exists = savedAccounts.some((account) => account.email === email);
        if (!exists) {
          const newAccounts = [...savedAccounts, { email, password }];
          setSavedAccounts(newAccounts);
          localStorage.setItem("savedAccounts", JSON.stringify(newAccounts));
        }
        navigate("/dashboard/inbox");
      } else {
        setError(result.error);
        setLoading(false);
      }
    } catch (err) {
      console.error("Login failed:", err);
      setError("An error occurred during login");
      setLoading(false);
    }
  };

  return (
    <>
      <div className="flex items-center justify-center h-full flex-1 bg-[#181818]">
        <div className="bg-[#232323] p-8 rounded-lg shadow-lg w-full h-full max-w-md">
          <h2 className="text-2xl font-bold mb-6 text-center text-[#FFFFFF]">
            Login
          </h2>
          <form onSubmit={handleLogin} className="flex flex-col gap-2 w-full">
            {savedAccounts.length > 0 && (
              <button
                type="button"
                onClick={() => setShowAccounts(true)}
                className="mb-2 text-xs text-[#B3B3B3] hover:text-[#FFFFFF] underline self-start"
              >
                Show Saved Accounts
              </button>
            )}
            <div className="flex flex-col gap-2 max-w-md min-w-sm">
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="Email"
                className="w-full p-3 bg-[#1E1E1E] text-[#FFFFFF] border border-[#333333] rounded-lg focus:ring-2 focus:ring-[#3D3D3D] focus:outline-none placeholder-[#B3B3B3]"
              />
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Password"
                className="w-full p-3 bg-[#1E1E1E] text-[#FFFFFF] border border-[#333333] rounded-lg focus:ring-2 focus:ring-[#3D3D3D] focus:outline-none placeholder-[#B3B3B3]"
              />
              <div className="flex py-1 gap-1 items-center justify-start text-text-primary">
                <Info size={16} color="red" />
                <p className="text-xs ">
                  use app password if you have 2 step verification enabled
                </p>
              </div>
            </div>
            {error && <p className="text-red-500 text-sm">{error}</p>}
            <button
              disabled={loading}
              type="submit"
              className={`w-full bg-[#4A4A4A] text-[#FFFFFF] py-3 px-4 rounded-lg hover:bg-[#3D3D3D] transition-colors duration-200 font-medium disabled:opacity-50 disabled:cursor-not-allowed `}
            >
              {loading ? "signing you in..." : "Login"}
            </button>
          </form>

          {/* Popup Modal for Saved Accounts */}
          {showAccounts && (
            <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 transition-opacity duration-300 ease-out">
              <div className="bg-[#232323] rounded-lg p-6 min-w-[300px] relative transform transition-all duration-300 ease-out scale-95 opacity-100 translate-y-0 animate-fade-in">
                <button
                  className="absolute top-2 right-2 text-[#B3B3B3] hover:text-[#FFFFFF] transition-colors duration-200"
                  onClick={() => setShowAccounts(false)}
                >
                  <X size={20} />
                </button>
                <h3 className="text-lg font-semibold mb-4 text-[#FFFFFF]">
                  Saved Accounts
                </h3>
                <div className="flex flex-col gap-2">
                  {savedAccounts.map((account, idx) => (
                    <button
                      key={idx}
                      className="text-left px-3 py-2 rounded bg-[#1E1E1E] text-[#B3B3B3] hover:bg-[#333] hover:text-[#FFF] transition-colors duration-200"
                      onClick={() => {
                        setEmail(account.email);
                        setPassword(account.password);
                        setShowAccounts(false);
                      }}
                    >
                      {account.email}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
      <Footer />
    </>
  );
}
