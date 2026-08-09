import React from "react";
import { useNavigate } from "react-router-dom";
import "./Results.css";

function Results() {
  const navigate = useNavigate();

  const result = JSON.parse(
    sessionStorage.getItem("latestAnalysis")
  );

  if (!result) {
    return (
      <div className="no-results">

        <div className="no-results-icon">
          📊
        </div>

        <h2>No Analysis Available</h2>

        <p>
          Analyze two cosmetic products to view results.
        </p>

        <button
          onClick={() => navigate("/dashboard/analyze")}
        >
          Start Analysis
        </button>

      </div>
    );
  }

  const prediction =
    result.safety_prediction ||
    result.prediction ||
    "Medium Risk";

  const normalizedPrediction =
    prediction.toLowerCase();

  let predictionClass = "medium-risk";

  if (normalizedPrediction.includes("safe")) {
    predictionClass = "safe";
  } else if (
    normalizedPrediction.includes("harmful")
  ) {
    predictionClass = "harmful";
  }

  return (
    <div className="results-page">

      <div className="results-heading">

        <p>ANALYSIS COMPLETE</p>

        <h1>Analysis Results</h1>

        <span>
          Ingredient conflicts and safety prediction
        </span>

      </div>

      <div
        className={`prediction-card ${predictionClass}`}
      >

        <div className="prediction-icon">
          {predictionClass === "safe"
            ? "✓"
            : predictionClass === "harmful"
            ? "!"
            : "⚠"}
        </div>

        <div>
          <p>SAFETY PREDICTION</p>

          <h2>
            {prediction}
          </h2>
        </div>

      </div>

      <div className="results-grid">

        <div className="result-section">

          <h2>Product 1 Ingredients</h2>

          <ul>
            {(result.product1_ingredients || []).map(
              (ingredient, index) => (
                <li key={index}>
                  ✓ {ingredient}
                </li>
              )
            )}
          </ul>

        </div>

        <div className="result-section">

          <h2>Product 2 Ingredients</h2>

          <ul>
            {(result.product2_ingredients || []).map(
              (ingredient, index) => (
                <li key={index}>
                  ✓ {ingredient}
                </li>
              )
            )}
          </ul>

        </div>

      </div>

      <div className="conflict-section">

        <h2>Ingredient Conflicts</h2>

        {result.conflicts &&
        result.conflicts.length > 0 ? (

          <div className="conflict-list">

            {result.conflicts.map(
              (conflict, index) => (

                <div
                  className="conflict-item"
                  key={index}
                >
                  <span>⚠️</span>

                  <div>
                    <strong>
                      Conflict Detected
                    </strong>

                    <p>
                      {typeof conflict === "string"
                        ? conflict
                        : conflict.description ||
                          conflict.message}
                    </p>
                  </div>

                </div>

              )
            )}

          </div>

        ) : (

          <div className="no-conflict">
            ✓ No ingredient conflicts detected.
          </div>

        )}

      </div>

      <div className="result-actions">

        <button
          onClick={() =>
            navigate("/dashboard/analyze")
          }
        >
          Analyze Another
        </button>

        <button
          onClick={() =>
            navigate("/dashboard/history")
          }
        >
          View History
        </button>

      </div>

    </div>
  );
}

export default Results;