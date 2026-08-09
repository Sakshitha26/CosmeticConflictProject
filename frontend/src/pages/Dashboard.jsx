import React from "react";
import { useNavigate } from "react-router-dom";
import "./Dashboard.css";

function Dashboard() {
  const navigate = useNavigate();

  const user = JSON.parse(
    localStorage.getItem("currentUser")
  );

  const history =
    JSON.parse(localStorage.getItem("analysisHistory")) || [];

  return (
    <div className="dashboard-page">

      <div className="welcome-section">

        <div>
          <p className="dashboard-label">
            WELCOME BACK
          </p>

          <h1>
            Hello, {user?.name || "User"} 👋
          </h1>

          <p>
            Analyze cosmetic ingredients and check for potential conflicts.
          </p>
        </div>

        <button
          className="start-analysis"
          onClick={() => navigate("/dashboard/analyze")}
        >
          + New Analysis
        </button>

      </div>

      <div className="dashboard-cards">

        <div className="dashboard-card">
          <span>🔬</span>
          <h3>Analyze Products</h3>
          <p>
            Upload two ingredient images to compare their ingredients.
          </p>

          <button
            onClick={() => navigate("/dashboard/analyze")}
          >
            Start Analysis →
          </button>
        </div>

        <div className="dashboard-card">
          <span>📊</span>
          <h3>Latest Results</h3>
          <p>
            View your latest cosmetic safety prediction.
          </p>

          <button
            onClick={() => navigate("/dashboard/results")}
          >
            View Results →
          </button>
        </div>

        <div className="dashboard-card">
          <span>🕘</span>
          <h3>Analysis History</h3>
          <p>
            View your previously analyzed products.
          </p>

          <button
            onClick={() => navigate("/dashboard/history")}
          >
            View History →
          </button>
        </div>

      </div>

      <div className="dashboard-info">

        <h2>How It Works</h2>

        <div className="workflow">

          <div>
            <strong>1</strong>
            <span>Upload Images</span>
          </div>

          <div>
            <strong>2</strong>
            <span>OCR Extraction</span>
          </div>

          <div>
            <strong>3</strong>
            <span>Conflict Detection</span>
          </div>

          <div>
            <strong>4</strong>
            <span>Safety Prediction</span>
          </div>

        </div>

        {history.length > 0 && (
          <p className="analysis-count">
            Total analyses: {history.length}
          </p>
        )}

      </div>

    </div>
  );
}

export default Dashboard;