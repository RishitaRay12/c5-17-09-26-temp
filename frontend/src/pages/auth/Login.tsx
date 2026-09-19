import {
  useState,
  type FormEvent,
} from "react";

import {
  Link,
  useLocation,
  useNavigate,
} from "react-router-dom";
import axios from "axios";

import { useAuth } from "../../context/AuthContext";
import "./Auth.css";

function Login() {
  const navigate = useNavigate();
  const location = useLocation();

  const { login, loading } = useAuth();

  const [username, setUsername] =
    useState("");

  const [password, setPassword] =
    useState("");

  const [error, setError] =
    useState("");

  const from =
    (
      location.state as {
        from?: {
          pathname: string;
        };
      } | null
    )?.from?.pathname || "/dashboard";

  const handleSubmit = async (
    event: FormEvent<HTMLFormElement>
  ) => {
    event.preventDefault();

    setError("");

    try {
      await login(
        username,
        password
      );

      // Only navigate after login succeeds
      navigate(from, {
        replace: true,
      });
    } catch (err: unknown) {
      const errorMessage = axios.isAxiosError(err)
        ? err.response?.data?.detail ||
          (err.code === "ERR_NETWORK"
            ? "Unable to connect to the server. Please try again."
            : err.message)
        : err instanceof Error
          ? err.message
          : "Invalid username or password.";

      setError(
        errorMessage
      );
    }
  };

  return (
    <div className="auth-page">

      <div className="auth-container">

        <div className="auth-header">

          <div className="auth-logo">
            🚀
          </div>

          <h1>
            Retail Policy Intelligence and Decision Support System
          </h1>

          <h2>
            Welcome Back
          </h2>

          <p>
            Sign in to continue to your
            startup workspace.
          </p>

        </div>

        {error && (
          <div className="auth-error">
            {error}
          </div>
        )}

        <form
          className="auth-form"
          onSubmit={handleSubmit}
        >

          <div className="form-group">

            <label htmlFor="username">
              Username
            </label>

            <input
              id="username"
              type="text"
              value={username}
              onChange={(event) =>
                setUsername(
                  event.target.value
                )
              }
              placeholder="Enter your username"
              required
            />

          </div>

          <div className="form-group">

            <label htmlFor="password">
              Password
            </label>

            <input
              id="password"
              type="password"
              value={password}
              onChange={(event) =>
                setPassword(
                  event.target.value
                )
              }
              placeholder="Enter your password"
              required
            />

          </div>

          <button
            type="submit"
            className="auth-button"
            disabled={loading}
          >
            {loading
              ? "Logging in..."
              : "Log In"}
          </button>

        </form>

        <div className="auth-footer">

          <span>
            Don't have an account?
          </span>

          <Link to="/register">
            Register
          </Link>

        </div>

      </div>

    </div>
  );
}

export default Login;