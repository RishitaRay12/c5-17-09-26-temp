import {
  createContext,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";

import axios from "axios";

interface User {
  id?: number;
  username?: string;
  name?: string;
  email?: string;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  loading: boolean;

  login: (
    username: string,
    password: string
  ) => Promise<void>;

  register: (
    username: string,
    name: string,
    email: string,
    password: string
  ) => Promise<void>;

  logout: () => void;

  isAuthenticated: boolean;
}

const AuthContext =
  createContext<AuthContextType | undefined>(
    undefined
  );

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  "http://127.0.0.1:8000";

export function AuthProvider({
  children,
}: {
  children: ReactNode;
}) {
  const [token, setToken] =
    useState<string | null>(
      localStorage.getItem("token")
    );

  const [user, setUser] =
    useState<User | null>(null);

  const [loading, setLoading] =
    useState(false);

  // ==========================================
  // Load logged-in user when app starts
  // ==========================================

  useEffect(() => {
    const loadCurrentUser = async () => {
      const storedToken =
        localStorage.getItem("token");

      if (!storedToken) {
        return;
      }

      try {
        setToken(storedToken);

        const response =
          await axios.get(
            `${API_BASE_URL}/users/me`,
            {
              headers: {
                Authorization:
                  `Bearer ${storedToken}`,
              },
            }
          );

        setUser(response.data);
      } catch (error) {
        console.error(
          "Failed to load current user:",
          error
        );

        localStorage.removeItem("token");
        setToken(null);
        setUser(null);
      }
    };

    loadCurrentUser();
  }, []);

  // ==========================================
  // LOGIN
  // ==========================================

  const login = async (
    username: string,
    password: string
  ) => {
    setLoading(true);

    try {
      // Username is still used for authentication
      const body = new URLSearchParams();

      body.append("username", username);
      body.append("password", password);

      const response =
        await axios.post(
          `${API_BASE_URL}/users/login`,
          body,
          {
            headers: {
              "Content-Type":
                "application/x-www-form-urlencoded",
            },
          }
        );

      const accessToken =
        response.data.access_token;

      // Save JWT
      localStorage.setItem(
        "token",
        accessToken
      );

      setToken(accessToken);

      // ========================================
      // Get complete user information
      // ========================================

      const userResponse =
        await axios.get(
          `${API_BASE_URL}/users/me`,
          {
            headers: {
              Authorization:
                `Bearer ${accessToken}`,
            },
          }
        );

      setUser(userResponse.data);
    } finally {
      setLoading(false);
    }
  };

  // ==========================================
  // REGISTER
  // ==========================================

  const register = async (
    username: string,
    name: string,
    email: string,
    password: string
  ) => {
    setLoading(true);

    try {
      await axios.post(
        `${API_BASE_URL}/users/register`,
        {
          username,
          name,
          email,
          password,
        },
        {
          headers: {
            "Content-Type":
              "application/json",
          },
        }
      );
    } finally {
      setLoading(false);
    }
  };

  // ==========================================
  // LOGOUT
  // ==========================================

  const logout = () => {
    localStorage.removeItem("token");

    setToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        loading,
        login,
        register,
        logout,
        isAuthenticated: !!token,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

// ==========================================
// Hook
// ==========================================

export function useAuth() {
  const context =
    useContext(AuthContext);

  if (!context) {
    throw new Error(
      "useAuth must be used inside AuthProvider"
    );
  }

  return context;
}