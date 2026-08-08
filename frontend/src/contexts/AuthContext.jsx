import React, { createContext, useContext, useState, useEffect } from "react";

const AuthContext = createContext(null);

// Simple hash function using Web Crypto API
async function hashPassword(password) {
  const encoder = new TextEncoder();
  const data = encoder.encode(password);
  const hashBuffer = await crypto.subtle.digest("SHA-256", data);
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  return hashArray.map((b) => b.toString(16).padStart(2, "0")).join("");
}

export function AuthProvider({ children }) {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  // Check for existing session on mount
  useEffect(() => {
    const session = localStorage.getItem("admin_session");
    if (session) {
      try {
        const { expiry } = JSON.parse(session);
        if (expiry && new Date().getTime() < expiry) {
          setIsAuthenticated(true);
        } else {
          localStorage.removeItem("admin_session");
        }
      } catch {
        localStorage.removeItem("admin_session");
      }
    }
    setIsLoading(false);
  }, []);

  const login = async (username, password) => {
    const adminUsername = process.env.REACT_APP_ADMIN_USERNAME;
    const adminPasswordHash = process.env.REACT_APP_ADMIN_PASSWORD_HASH;

    if (!adminUsername || !adminPasswordHash) {
      return { success: false, error: "Admin credentials not configured" };
    }

    const inputHash = await hashPassword(password);

    if (username === adminUsername && inputHash === adminPasswordHash) {
      // Session expires in 24 hours
      const expiry = new Date().getTime() + 24 * 60 * 60 * 1000;
      localStorage.setItem("admin_session", JSON.stringify({ expiry }));
      setIsAuthenticated(true);
      return { success: true };
    }

    return { success: false, error: "Invalid username or password" };
  };

  const logout = () => {
    localStorage.removeItem("admin_session");
    setIsAuthenticated(false);
  };

  return (
    <AuthContext.Provider value={{ isAuthenticated, isLoading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}

// Utility function to generate password hash (for setup)
export { hashPassword };

