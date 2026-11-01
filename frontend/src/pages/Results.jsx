
import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./Results.css";

function Results() {
  const navigate = useNavigate();

  const [whatIfResults, setWhatIfResults] = useState({});
  const [loadingIndex, setLoadingIndex] = useState(null);
  const [errors, setErrors] = useState({});

  const storedResult = sessionStorage.getItem("latestAnalysis");

  let result = null;

  try {
    result = storedResult ? JSON.parse(storedResult) : null;
  } catch (error) {
    console.error("Unable to read analysis result:", error);
  }

  // ==========================================
  // NO RESULT
  // ==========================================

  if (!result) {
    return (
      <div className="results-page">
        <div className="no-results">
          <div className="no-results-icon">📊</div>
          <h2>No Analysis Available</h2>
          <p>
            Analyze two cosmetic products to view their
            ingredient compatibility results.
          </p>
          <button onClick={() => navigate("/dashboard/analyze")}>
            Start Analysis
          </button>
        </div>
      </div>
    );
  }

  // ==========================================
  // PRODUCT INGREDIENTS
  // ==========================================

  const product1Ingredients =
    result.product1?.ingredients ||
    result.product1_ingredients ||
    [];

  const product2Ingredients =
    result.product2?.ingredients ||
    result.product2_ingredients ||
    [];

  const product1Matched =
    result.product1?.matched_ingredients || [];

  const product2Matched =
    result.product2?.matched_ingredients || [];

  const matchedIngredients = [
    ...new Set([
      ...product1Matched,
      ...product2Matched
    ])
  ];

  const ingredients =
    result.ingredients ||
    [...new Set([
      ...product1Ingredients,
      ...product2Ingredients
    ])];

  // ==========================================
  // CONFLICTS
  // ==========================================

  const conflicts = Array.isArray(result.conflicts)
    ? result.conflicts
    : [];

  // ==========================================
  // ORIGINAL RISK ANALYSIS
  // ==========================================

  const originalAnalysis = result.risk_analysis || {};

  const originalCCI = originalAnalysis.cci_score ?? "N/A";

  const originalRisk =
    originalAnalysis.risk_level ||
    result.overall_severity ||
    "Unknown";

  // ==========================================
  // OVERALL SEVERITY
  // ==========================================

  const severity = String(
    result.overall_severity ||
    result.safety_prediction ||
    result.prediction ||
    "safe"
  ).toLowerCase();

  const status =
    result.status ||
    (
      severity === "safe" || severity === "none"
        ? "SAFE"
        : severity === "high"
        ? "WARNING"
        : "CAUTION"
    );

  let predictionClass = "safe";
  let predictionIcon = "✓";
  let predictionText = "Safe";

  if (severity === "high") {
    predictionClass = "harmful";
    predictionIcon = "!";
    predictionText = "High Risk";
  } else if (severity === "medium") {
    predictionClass = "medium-risk";
    predictionIcon = "⚠";
    predictionText = "Medium Risk";
  } else if (severity === "low") {
    predictionClass = "medium-risk";
    predictionIcon = "⚠";
    predictionText = "Low Risk";
  }

  // ==========================================
  // WHAT-IF ANALYSIS FUNCTION
  // ==========================================

  const handleWhatIf = async (conflict, index) => {
    setLoadingIndex(index);

    setErrors((previous) => ({
      ...previous,
      [index]: ""
    }));

    try {
      const response = await fetch(
        "http://127.0.0.1:5000/api/what-if",
        {
          method: "POST",

          headers: {
            "Content-Type": "application/json"
          },

          body: JSON.stringify({
            ingredients: ingredients,
            conflicts: conflicts,

            selected_ingredient_1:
              conflict.ingredient_1,

            selected_ingredient_2:
              conflict.ingredient_2
          })
        }
      );

      const data = await response.json();

      if (!response.ok || !data.success) {
        throw new Error(
          data.error || "What-If analysis failed."
        );
      }

      setWhatIfResults((previous) => ({
        ...previous,
        [index]: data
      }));

    } catch (error) {
      console.error("What-If Error:", error);

      setErrors((previous) => ({
        ...previous,
        [index]: error.message
      }));

    } finally {
      setLoadingIndex(null);
    }
  };

  // ==========================================
  // RENDER RESULTS
  // ==========================================

  return (
    <div className="results-page">

      {/* HEADER */}

      <div className="results-heading">
        <p>ANALYSIS COMPLETE</p>
        <h1>Analysis Results</h1>
        <span>
          Ingredient compatibility and safety analysis
        </span>
      </div>

      {/* SAFETY CARD */}

      <div className={`prediction-card ${predictionClass}`}>
        <div className="prediction-icon">
          {predictionIcon}
        </div>

        <div>
          <p>OVERALL SAFETY</p>
          <h2>{predictionText}</h2>
          <span>Status: {status}</span>
        </div>
      </div>

      {/* ORIGINAL CCI */}

      <div className="conflict-section">
        <h2>📊 Original Risk Analysis</h2>

        <p>
          Original CCI Score: <strong>{originalCCI}</strong>
        </p>

        <p>
          Original Risk Level: <strong>{originalRisk}</strong>
        </p>
      </div>

      {/* PRODUCT INGREDIENTS */}

      <div className="results-grid">

        <div className="result-section">
          <h2>🧴 Product 1 Ingredients</h2>

          <p className="ingredient-count">
            {product1Ingredients.length} ingredients detected
          </p>

          {product1Ingredients.length > 0 ? (
            <ul>
              {product1Ingredients.map((ingredient, index) => (
                <li key={index}>
                  <span>✓</span>
                  {ingredient}
                </li>
              ))}
            </ul>
          ) : (
            <p className="empty-message">
              No ingredients detected.
            </p>
          )}
        </div>

        <div className="result-section">
          <h2>🧴 Product 2 Ingredients</h2>

          <p className="ingredient-count">
            {product2Ingredients.length} ingredients detected
          </p>

          {product2Ingredients.length > 0 ? (
            <ul>
              {product2Ingredients.map((ingredient, index) => (
                <li key={index}>
                  <span>✓</span>
                  {ingredient}
                </li>
              ))}
            </ul>
          ) : (
            <p className="empty-message">
              No ingredients detected.
            </p>
          )}
        </div>

      </div>

      {/* MATCHED INGREDIENTS */}

      {matchedIngredients.length > 0 && (
        <div className="conflict-section">
          <h2>🔍 Matched Ingredients</h2>

          <p>
            Ingredients identified for compatibility analysis.
          </p>

          <div className="matched-ingredients">
            {matchedIngredients.map((ingredient, index) => (
              <span key={index}>{ingredient}</span>
            ))}
          </div>
        </div>
      )}

      {/* CONFLICT RESULTS */}

      <div className="conflict-section">

        <h2>
          {conflicts.length === 0
            ? "✓ Ingredient Compatibility"
            : "⚠ Ingredient Conflicts"}
        </h2>

        {conflicts.length === 0 ? (

          <div className="no-conflict">
            <span>✓</span>

            <div>
              <strong>
                No Ingredient Conflicts Detected
              </strong>

              <p>
                No conflicting ingredient combinations
                were found between these two products.
              </p>
            </div>
          </div>

        ) : (

          <div className="conflict-list">

            {conflicts.map((conflict, index) => {

              const conflictSeverity =
                String(conflict.severity || "unknown").toLowerCase();

              const simulation = whatIfResults[index];

              return (

                <div
                  className={`conflict-item ${conflictSeverity}`}
                  key={index}
                >

                  <div className="conflict-icon">
                    ⚠️
                  </div>

                  <div className="conflict-content">

                    <strong>
                      {conflict.ingredient_1}
                      {" + "}
                      {conflict.ingredient_2}
                    </strong>

                    <span className="conflict-severity">
                      {conflictSeverity.toUpperCase()}
                    </span>

                    {conflict.reason && (
                      <p>
                        <strong>Reason:</strong>{" "}
                        {conflict.reason}
                      </p>
                    )}

                    {conflict.recommendation && (
                      <p>
                        <strong>Recommendation:</strong>{" "}
                        {conflict.recommendation}
                      </p>
                    )}

                    {/* WHAT-IF BUTTON */}

                    <button
                      type="button"
                      onClick={() => handleWhatIf(conflict, index)}
                      disabled={loadingIndex !== null}
                      style={{
                        marginTop: "12px",
                        padding: "10px 18px",
                        borderRadius: "6px",
                        border: "none",
                        cursor:
                          loadingIndex !== null
                            ? "not-allowed"
                            : "pointer",
                        opacity:
                          loadingIndex !== null
                            ? 0.6
                            : 1
                      }}
                    >
                      {loadingIndex === index
                        ? "Calculating..."
                        : "What-If Analysis"}
                    </button>

                    {/* ERROR MESSAGE */}

                    {errors[index] && (
                      <p style={{ color: "red", marginTop: "10px" }}>
                        {errors[index]}
                      </p>
                    )}

                    {/* WHAT-IF RESULT */}

                    {simulation && (

                      <div
                        className="what-if-result"
                        style={{
                          marginTop: "18px",
                          padding: "16px",
                          border: "1px solid #ccc",
                          borderRadius: "8px",
                          background: "#f8f9fa",
                          color: "#222"
                        }}
                      >

                        <h3>What-If Simulation Result</h3>

                        <p>
                          <strong>Excluded Pair:</strong>{" "}
                          {simulation.excluded_pair.ingredient_1}
                          {" + "}
                          {simulation.excluded_pair.ingredient_2}
                        </p>

                        <hr />

                        <h4>Original Analysis</h4>

                        <p>
                          Original CCI:{" "}
                          <strong>
                            {simulation.original_cci}
                          </strong>
                        </p>

                        <p>
                          Original Risk:{" "}
                          <strong>
                            {simulation.original_risk}
                          </strong>
                        </p>

                        <hr />

                        <h4>Updated What-If Analysis</h4>

                        <p>
                          Updated CCI:{" "}
                          <strong>
                            {simulation.updated_cci}
                          </strong>
                        </p>

                        <p>
                          Updated Risk:{" "}
                          <strong>
                            {simulation.updated_risk}
                          </strong>
                        </p>

                        <p>
                          Conflicts Before:{" "}
                          <strong>
                            {simulation.original_conflict_count}
                          </strong>
                        </p>

                        <p>
                          Conflicts After:{" "}
                          <strong>
                            {simulation.remaining_conflict_count}
                          </strong>
                        </p>

                        <h4>Remaining Conflicts</h4>

                        {simulation.remaining_conflicts.length > 0 ? (

                          <ul>
                            {simulation.remaining_conflicts.map(
                              (remaining, remainingIndex) => (
                                <li key={remainingIndex}>
                                  {remaining.ingredient_1}
                                  {" + "}
                                  {remaining.ingredient_2}
                                  {" ("}
                                  {remaining.severity}
                                  {")"}
                                </li>
                              )
                            )}
                          </ul>

                        ) : (

                          <p>
                            No conflicts remain after exclusion.
                          </p>

                        )}

                        <p style={{ marginTop: "12px" }}>
                          <strong>Recommendation:</strong>{" "}
                          {simulation.updated_analysis.recommendation}
                        </p>

                      </div>

                    )}

                  </div>

                </div>

              );

            })}

          </div>

        )}

      </div>

      {/* ANALYSIS SUMMARY */}

      <div className="result-summary">

        <div className="summary-header">
          <p>OVERVIEW</p>
          <h2>📋 Analysis Summary</h2>
        </div>

        <div className="summary-grid">

          <div className="summary-card">
            <div className="summary-number">
              {product1Ingredients.length}
            </div>

            <div className="summary-label">
              Product 1
              <span>Ingredients</span>
            </div>
          </div>

          <div className="summary-card">
            <div className="summary-number">
              {product2Ingredients.length}
            </div>

            <div className="summary-label">
              Product 2
              <span>Ingredients</span>
            </div>
          </div>

          <div className="summary-card">
            <div className="summary-number">
              {conflicts.length}
            </div>

            <div className="summary-label">
              Conflicts
              <span>Found</span>
            </div>
          </div>

          <div className="summary-card severity-card">
            <div className="summary-number">
              {severity.toUpperCase()}
            </div>

            <div className="summary-label">
              Overall
              <span>Severity</span>
            </div>
          </div>

        </div>

      </div>

      {/* ACTION BUTTONS */}

      <div className="result-actions">

        <button
          onClick={() => navigate("/dashboard/analyze")}
        >
          Analyze Another
        </button>

        <button
          onClick={() => navigate("/dashboard/history")}
        >
          View History
        </button>

      </div>

    </div>
  );
}

export default Results;
