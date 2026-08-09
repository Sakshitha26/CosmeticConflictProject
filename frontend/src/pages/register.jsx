import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./Register.css";

function Register() {
  const navigate = useNavigate();

  const [form, setForm] = useState({
    name: "",
    email: "",
    password: "",
    confirmPassword: ""
  });

  const [error, setError] = useState("");

  const handleChange = (e) => {
    setForm({
      ...form,
      [e.target.name]: e.target.value
    });

    setError("");
  };

  const validatePassword = (password) => {
    return (
      password.length >= 8 &&
      /[A-Z]/.test(password) &&
      /[a-z]/.test(password) &&
      /[0-9]/.test(password) &&
      /[!@#$%^&*]/.test(password)
    );
  };

  const handleRegister = (e) => {
    e.preventDefault();

    if (!form.name.trim()) {
      setError("Please enter your name.");
      return;
    }

    if (!form.email.includes("@")) {
      setError("Please enter a valid email.");
      return;
    }

    if (!validatePassword(form.password)) {
      setError(
        "Password must contain 8 characters, uppercase, lowercase, number and special character."
      );
      return;
    }

    if (form.password !== form.confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    const users = JSON.parse(localStorage.getItem("users")) || [];

    const existingUser = users.find(
      (user) => user.email === form.email
    );

    if (existingUser) {
      setError("User already registered. Please login.");
      return;
    }

    users.push({
      name: form.name,
      email: form.email,
      password: form.password
    });

    localStorage.setItem("users", JSON.stringify(users));

    alert("Registration successful! Please login.");

    navigate("/login");
  };

  return (
    <div className="register-page">

      <div className="register-card">

        <div className="register-logo">✦</div>

        <h1>Create Account</h1>

        <p className="register-subtitle">
          Create your CosmeticConflict account
        </p>

        <form onSubmit={handleRegister}>

          <label>Name</label>
          <input
            type="text"
            name="name"
            placeholder="Enter your name"
            value={form.name}
            onChange={handleChange}
          />

          <label>Email</label>
          <input
            type="email"
            name="email"
            placeholder="Enter your email"
            value={form.email}
            onChange={handleChange}
          />

          <label>Password</label>
          <input
            type="password"
            name="password"
            placeholder="Create a password"
            value={form.password}
            onChange={handleChange}
          />

          <small className="password-info">
            8+ characters, uppercase, lowercase, number & special character
          </small>

          <label>Confirm Password</label>
          <input
            type="password"
            name="confirmPassword"
            placeholder="Confirm password"
            value={form.confirmPassword}
            onChange={handleChange}
          />

          {error && (
            <p className="form-error">
              {error}
            </p>
          )}

          <button className="register-submit">
            Register
          </button>

        </form>

        <p className="switch-text">
          Already have an account?
          <button onClick={() => navigate("/login")}>
            Login
          </button>
        </p>

      </div>

    </div>
  );
}

export default Register;