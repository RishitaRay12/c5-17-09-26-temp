import {
  useState,
  type FormEvent,
} from "react";

import {
  Link,
  useNavigate,
} from "react-router-dom";
import axios from "axios";

import { useAuth } from "../../context/AuthContext";
import "./Auth.css";

function Register() {
  const navigate = useNavigate();

  const { register, loading } =
    useAuth();

  const [username, setUsername] =
    useState("");

  const [name, setName] =
    useState("");

  const [email, setEmail] =
    useState("");

  const [password, setPassword] =
    useState("");

  const [confirmPassword, setConfirmPassword] =
    useState("");

  const [error, setError] =
    useState("");

  const [success, setSuccess] =
    useState("");

  const handleSubmit = async (
    event: FormEvent<HTMLFormElement>
  ) => {
    event.preventDefault();

    setError("");
    setSuccess("");

    if (
      password !== confirmPassword
    ) {
      setError(
        "Passwords do not match."
      );
      return;
    }

    try {
      await register(
        username,
        name,
        email,
        password
      );

      setSuccess(
        "Account created successfully. Please log in."
      );

      setTimeout(() => {
        navigate("/login");
      }, 1000);
    } catch (err: unknown) {
      setError(
        (axios.isAxiosError(err) &&
          (err.response?.data?.detail || err.message)) ||
          (err instanceof Error ? err.message : "") ||
          "Registration failed."
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
            Create an Account
          </h2>

          <p>
            Start building and evaluating
            your startup ideas.
          </p>

        </div>

        {error && (
          <div className="auth-error">
            {error}
          </div>
        )}

        {success && (
          <div className="auth-success">
            {success}
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
              placeholder="Choose a username"
              required
            />

          </div>

          <div className="form-group">

            <label htmlFor="name">
              Full Name
            </label>

            <input
              id="name"
              type="text"
              value={name}
              onChange={(event) =>
                setName(
                  event.target.value
                )
              }
              placeholder="John Doe"
              required
            />

          </div>

          <div className="form-group">

            <label htmlFor="email">
              Email
            </label>

            <input
              id="email"
              type="email"
              value={email}
              onChange={(event) =>
                setEmail(
                  event.target.value
                )
              }
              placeholder="name@example.com"
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
              placeholder="••••••••"
              required
            />

          </div>

          <div className="form-group">

            <label htmlFor="confirmPassword">
              Confirm Password
            </label>

            <input
              id="confirmPassword"
              type="password"
              value={confirmPassword}
              onChange={(event) =>
                setConfirmPassword(
                  event.target.value
                )
              }
              placeholder="••••••••"
              required
            />

          </div>

          <button
            type="submit"
            className="auth-button"
            disabled={loading}
          >
            {loading
              ? "Creating Account..."
              : "Register"}
          </button>

        </form>

        <div className="auth-footer">

          <span>
            Already have an account?
          </span>

          <Link to="/login">
            Sign In
          </Link>

        </div>

      </div>

    </div>
  );
}

export default Register;