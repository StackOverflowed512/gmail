import { createContext, useContext, useState, useEffect } from "react";

const AuthContext = createContext();

export const useAuth = () => {
  return useContext(AuthContext);
};

export const AuthProvider = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);
  const [user, setUser] = useState({});
  const [inbox, setInbox] = useState([]);
  const [sent, setSent] = useState([]);
  const [fetchingMail, setFetching] = useState(true);

  useEffect(() => {
    checkAuthStatus();
  }, []);

  const checkAuthStatus = async () => {
    try {
      const response = await fetch("/api/current_user", {
        method: "GET",
        headers: {
          Authorization: `Bearer ${localStorage.getItem("access_token")}`,
          "Content-Type": "application/json",
        },
      });

      if (response.ok) {
        const data = await response.json();
        setUser(data);
        setIsAuthenticated(true);
      } else {
        setIsAuthenticated(false);
        setUser(null);
      }
    } catch (error) {
      console.error("Auth check failed:", error);
      setIsAuthenticated(false);
      setUser(null);
    } finally {
      setLoading(false);
    }
  };
  const login = async (email, password) => {
    try {
      const response = await fetch("/api/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email, password }),
      });

      const result = await response.json();

      if (response.ok) {
        localStorage.setItem("access_token", result.access_token);
        await checkAuthStatus();
        return { success: true };
      } else {
        return {
          success: false,
          error: "Invalid credentials",
        };
      }
    } catch (error) {
      console.error("Login failed:", error);
      return {
        success: false,
        error: "Login failed. Please try again.",
      };
    }
  };

  const logout = async () => {
    try {
      localStorage.removeItem("access_token");
      setIsAuthenticated(false);
      setUser(null);
    } catch (error) {
      console.error("Logout failed:", error);
    }
  };
  const getInbox = async ({ page = 1, per_page = 10 }) => {
    setFetching(true);
    if (isAuthenticated) {
      try {
        const response = await fetch(
          `/api/inbox?page=${page}&per_page=${per_page}`,
          {
            method: "GET",
            headers: {
              Authorization: `Bearer ${localStorage.getItem("access_token")}`,
              "Content-Type": "application/json",
            },
          }
        );
        if (response.ok) {
          const data = await response.json().then((data) => data.emails);
          setInbox(data);
          setFetching(false);
        }
      } catch (error) {
        console.error("Inbox failed:", error);
        setFetching(false);
      }
    }
  };

  const sentMails = async ({ page = 1, per_page = 10 }) => {
    setFetching(true);
    if (isAuthenticated) {
      try {
        const response = await fetch(
          `/api/sentbox?page=${page}&per_page=${per_page}`,
          {
            method: "GET",
            headers: {
              Authorization: `Bearer ${localStorage.getItem("access_token")}`,
              "Content-Type": "application/json",
            },
          }
        );
        if (response.ok) {
          const data = await response.json().then((data) => data.emails);
          setSent(data);
          setFetching(false);
        }
      } catch (error) {
        console.error("Sent mails failed:", error);
        setFetching(false);
      }
    }
  }

  const value = {
    isAuthenticated,
    loading,
    user,
    inbox,
    getInbox,
    sent,
    sentMails,
    login,
    logout,
    checkAuthStatus,
    fetchingMail,
  };

  return (
    <AuthContext.Provider value={value}>
      {!loading && children}
    </AuthContext.Provider>
  );
};
