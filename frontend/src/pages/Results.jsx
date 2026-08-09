import React from "react";
import { useNavigate } from "react-router-dom";
import "./Results.css";

function Results() {
  const navigate = useNavigate();

  const storedResult = sessionStorage.getItem("latestAnalysis");

  const result = storedResult
    ? JSON.parse(storedResult)
    : null;

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

          <button
            onClick={() =>
              navigate("/dashboard/analyze")
            }
          >
            Start Analysis
          </button>
        </div>
      </div>
    );
  }

  // ==========================================
  // PRODUCT 1 INGREDIENTS
  // ==========================================

  const product1Ingredients =
    result.product1?.ingredients ||
    result.product1_ingredients ||
    [];

  // ==========================================
  // PRODUCT 2 INGREDIENTS
  // ==========================================

  const product2Ingredients =
    result.product2?.ingredients ||
    result.product2_ingredients ||
    [];

  // ==========================================
  // MATCHED INGREDIENTS
  // ==========================================

  const product1Matched =
    result.product1?.matched_ingredients || [];

  const product2Matched =
    result.product2?.matched_ingredients || [];

  // Remove duplicates
  const matchedIngredients = [
    ...new Set([
      ...product1Matched,
      ...product2Matched
    ])
  ];

  // ==========================================
  // CONFLICTS
  // ==========================================

  const conflicts = Array.isArray(result.conflicts)
    ? result.conflicts
    : [];

  // ==========================================
  // OVERALL SEVERITY
  // ==========================================

  const severity = String(
    result.overall_severity ||
      result.safety_prediction ||
      result.prediction ||
      "safe"
  ).toLowerCase();

  // ==========================================
  // STATUS
  // ==========================================

  const status =
    result.status ||
    (severity === "safe" || severity === "none"
      ? "SAFE"
      : severity === "high"
      ? "WARNING"
      : "CAUTION");

  // ==========================================
  // SAFETY CARD
  // ==========================================

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
  } else {
    predictionClass = "safe";
    predictionIcon = "✓";
    predictionText = "Safe";
  }

  return (
    <div className="results-page">

      {/* ========================================= */}
      {/* HEADER */}
      {/* ========================================= */}

      <div className="results-heading">

        <p>ANALYSIS COMPLETE</p>

        <h1>Analysis Results</h1>

        <span>
          Ingredient compatibility and safety analysis
        </span>

      </div>


      {/* ========================================= */}
      {/* SAFETY CARD */}
      {/* ========================================= */}

      <div
        className={`prediction-card ${predictionClass}`}
      >

        <div className="prediction-icon">
          {predictionIcon}
        </div>

        <div>
          <p>OVERALL SAFETY</p>

          <h2>
            {predictionText}
          </h2>

          <span>
            Status: {status}
          </span>
        </div>

      </div>


      {/* ========================================= */}
      {/* PRODUCT INGREDIENTS */}
      {/* ========================================= */}

      <div className="results-grid">

        {/* PRODUCT 1 */}

        <div className="result-section">

          <h2>
            🧴 Product 1 Ingredients
          </h2>

          <p className="ingredient-count">
            {product1Ingredients.length} ingredients detected
          </p>

          {product1Ingredients.length > 0 ? (

            <ul>

              {product1Ingredients.map(
                (ingredient, index) => (

                  <li key={index}>
                    <span>✓</span>
                    {ingredient}
                  </li>

                )
              )}

            </ul>

          ) : (

            <p className="empty-message">
              No ingredients detected.
            </p>

          )}

        </div>


        {/* PRODUCT 2 */}

        <div className="result-section">

          <h2>
            🧴 Product 2 Ingredients
          </h2>

          <p className="ingredient-count">
            {product2Ingredients.length} ingredients detected
          </p>

          {product2Ingredients.length > 0 ? (

            <ul>

              {product2Ingredients.map(
                (ingredient, index) => (

                  <li key={index}>
                    <span>✓</span>
                    {ingredient}
                  </li>

                )
              )}

            </ul>

          ) : (

            <p className="empty-message">
              No ingredients detected.
            </p>

          )}

        </div>

      </div>


      {/* ========================================= */}
      {/* MATCHED INGREDIENTS */}
      {/* ========================================= */}

      {matchedIngredients.length > 0 && (

        <div className="conflict-section">

          <h2>
            🔍 Matched Ingredients
          </h2>

          <p>
            Ingredients identified for compatibility
            analysis.
          </p>

          <div className="matched-ingredients">

            {matchedIngredients.map(
              (ingredient, index) => (

                <span key={index}>
                  {ingredient}
                </span>

              )
            )}

          </div>

        </div>

      )}


      {/* ========================================= */}
      {/* CONFLICT RESULTS */}
      {/* ========================================= */}

      <div className="conflict-section">

        <h2>
          {conflicts.length === 0
            ? "✓ Ingredient Compatibility"
            : "⚠ Ingredient Conflicts"}
        </h2>


        {/* ======================================= */}
        {/* NO CONFLICT */}
        {/* ======================================= */}

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

          /* ===================================== */
          /* CONFLICT LIST */
          /* ===================================== */

          <div className="conflict-list">

            {conflicts.map(
              (conflict, index) => {

                const conflictSeverity =
                  String(
                    conflict.severity ||
                      "unknown"
                  ).toLowerCase();

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
                          <strong>
                            Reason:
                          </strong>{" "}
                          {conflict.reason}
                        </p>

                      )}


                      {conflict.recommendation && (

                        <p>
                          <strong>
                            Recommendation:
                          </strong>{" "}
                          {conflict.recommendation}
                        </p>

                      )}

                    </div>

                  </div>

                );
              }
            )}

          </div>

        )}

      </div>


      {/* ========================================= */}
      {/* ANALYSIS SUMMARY */}
      {/* ========================================= */}

      <div className="result-summary">

        <div className="summary-header">

          <p>OVERVIEW</p>

          <h2>
            📋 Analysis Summary
          </h2>

        </div>


        <div className="summary-grid">

          {/* PRODUCT 1 */}

          <div className="summary-card">

            <div className="summary-number">
              {product1Ingredients.length}
            </div>

            <div className="summary-label">
              Product 1
              <span>
                Ingredients
              </span>
            </div>

          </div>


          {/* PRODUCT 2 */}

          <div className="summary-card">

            <div className="summary-number">
              {product2Ingredients.length}
            </div>

            <div className="summary-label">
              Product 2
              <span>
                Ingredients
              </span>
            </div>

          </div>


          {/* CONFLICTS */}

          <div className="summary-card">

            <div className="summary-number">
              {conflicts.length}
            </div>

            <div className="summary-label">
              Conflicts
              <span>
                Found
              </span>
            </div>

          </div>


          {/* SEVERITY */}

          <div className="summary-card severity-card">

            <div className="summary-number">
              {severity.toUpperCase()}
            </div>

            <div className="summary-label">
              Overall
              <span>
                Severity
              </span>
            </div>

          </div>

        </div>

      </div>


      {/* ========================================= */}
      {/* ACTION BUTTONS */}
      {/* ========================================= */}

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