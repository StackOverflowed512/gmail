import { Info } from "lucide-react";
import { useState, useEffect } from "react";
import { useNavigate } from "react-router";
import { useAuth } from "../context/AuthContext";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { login } = useAuth();
  useEffect(() => {
    // Check if user is already authenticated
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
        navigate("/dashboard/inbox");
      } else {
        setError(result.error);
        setLoading(false);
      }
    } catch (err) {
      console.error("Login failed:", err);
      setError("An error occurred during login");
    }
  };
  return (
    <div className="w-screen h-screen bg-primary grid place-items-center">
      <div className=" flex flex-col gap-4 max-w-lg mx-auto mt-8 p-6 bg-[#121212] rounded-lg shadow-[0px_2px_10px_rgba(225,225,225,0.2)]">
        <h2 className="text-2xl font-bold  text-center text-[#FFFFFF]">
          Login With Email
        </h2>
        <form onSubmit={handleLogin} className="flex flex-col gap-2 w-full">
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
      </div>
    </div>
  );
}
