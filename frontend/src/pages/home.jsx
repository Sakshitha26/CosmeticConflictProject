import React from "react";
import { useNavigate } from "react-router-dom";
import "./Home.css";

function Home() {
  const navigate = useNavigate();

  return (
    <div className="home-page">

      <nav className="home-navbar">

        <div className="home-logo">
          <div className="logo-symbol">✦</div>
          <span>CosmeticConflict</span>
        </div>

        <div className="home-nav-buttons">
          <button
            className="nav-login"
            onClick={() => navigate("/login")}
          >
            Login
          </button>

          <button
            className="nav-register"
            onClick={() => navigate("/register")}
          >
            Register
          </button>
        </div>

      </nav>

      <section className="hero-section">

        <div className="hero-content">

          <p className="hero-small-title">
            SMART COSMETIC ANALYSIS
          </p>

          <h1>
            Know What Your
            <span> Cosmetics </span>
            Contain
          </h1>

          <p className="hero-description">
            Analyze cosmetic ingredients, detect ingredient conflicts,
            and understand whether a product is Safe, Medium Risk,
            or Harmful.
          </p>

          <div className="hero-buttons">

            <button
              className="hero-primary"
              onClick={() => navigate("/register")}
            >
              Get Started →
            </button>

            <button
              className="hero-secondary"
              onClick={() => navigate("/login")}
            >
              Login
            </button>

          </div>

        </div>

        <div className="hero-image-area">

          <div className="cosmetic-card card-one">
            <span>🧴</span>
          </div>

          <div className="cosmetic-card card-two">
            <span>🧪</span>
          </div>

          <div className="cosmetic-card card-three">
            <span>🌸</span>
          </div>

          <div className="hero-circle"></div>

        </div>

      </section>

      <section className="features-section">

        <h2>How CosmeticConflict Works</h2>

        <div className="features-grid">

          <div className="feature-card">
            <div className="feature-icon">📷</div>
            <h3>Upload</h3>
            <p>
              Upload ingredient images of cosmetic products.
            </p>
          </div>

          <div className="feature-card">
            <div className="feature-icon">🔍</div>
            <h3>Analyze</h3>
            <p>
              OCR extracts the ingredients from your images.
            </p>
          </div>

          <div className="feature-card">
            <div className="feature-icon">⚠️</div>
            <h3>Detect Conflicts</h3>
            <p>
              The system identifies potentially conflicting ingredients.
            </p>
          </div>

          <div className="feature-card">
            <div className="feature-icon">🛡️</div>
            <h3>Safety Prediction</h3>
            <p>
              Get a prediction: Safe, Medium Risk, or Harmful.
            </p>
          </div>

        </div>

      </section>

    </div>
  );
}

export default Home;