
import React from "react";
import { useNavigate } from "react-router-dom";
import "./Results.css";

function Results() {
  const navigate = useNavigate();

  const storedResult = sessionStorage.getItem("latestAnalysis");

  let result = null;

  try {
    result = storedResult ? JSON.parse(storedResult) : null;
  } catch (error) {
    console.error("Could not parse analysis result:", error);
  }

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

  // ==========================================
  // MATCHED INGREDIENTS
  // ==========================================

  const product1Matched =
    result.product1?.matched_ingredients || [];

  const product2Matched =
    result.product2?.matched_ingredients || [];

  const matchedIngredients = [
    ...new Set([...product1Matched, ...product2Matched])
  ];

  // ==========================================
  // CONFLICTS
  // ==========================================

  const conflicts = Array.isArray(result.conflicts)
    ? result.conflicts
    : [];

  // ==========================================
  // CONFLICT-SPECIFIC ML + SHAP RESULTS
  // ==========================================

  const conflictExplanations = Array.isArray(
    result.conflict_explanations
  )
    ? result.conflict_explanations
    : [];

  // Match a conflict with its ML explanation.
  // Ingredient order does not matter.

  const normalizeIngredient = (value) =>
    String(value || "").trim().toLowerCase();

  const getConflictExplanation = (conflict) => {
    const ingredient1 =
      conflict.ingredient_1 ||
      conflict.ingredient1 ||
      conflict.ingredient_a ||
      conflict.ingredientA;

    const ingredient2 =
      conflict.ingredient_2 ||
      conflict.ingredient2 ||
      conflict.ingredient_b ||
      conflict.ingredientB;

    return conflictExplanations.find((item) => {
      const sameOrder =
        normalizeIngredient(item.ingredient_1) ===
          normalizeIngredient(ingredient1) &&
        normalizeIngredient(item.ingredient_2) ===
          normalizeIngredient(ingredient2);

      const reverseOrder =
        normalizeIngredient(item.ingredient_1) ===
          normalizeIngredient(ingredient2) &&
        normalizeIngredient(item.ingredient_2) ===
          normalizeIngredient(ingredient1);

      return sameOrder || reverseOrder;
    });
  };

  // ==========================================
  // SEVERITY
  // ==========================================

  const severity = String(
    result.overall_severity ||
    result.safety_prediction ||
    result.prediction ||
    "safe"
  ).toLowerCase();

  const normalizedSeverity = severity.replace(/_/g, " ");

  const status =
    result.status ||
    (normalizedSeverity.includes("high")
      ? "WARNING"
      : normalizedSeverity.includes("medium") ||
        normalizedSeverity.includes("low")
      ? "CAUTION"
      : "SAFE");

  let predictionClass = "safe";
  let predictionIcon = "✓";
  let predictionText = "Safe";

  if (normalizedSeverity.includes("high")) {
    predictionClass = "harmful";
    predictionIcon = "!";
    predictionText = "High Risk";
  } else if (normalizedSeverity.includes("medium")) {
    predictionClass = "medium-risk";
    predictionIcon = "⚠";
    predictionText = "Medium Risk";
  } else if (normalizedSeverity.includes("low")) {
    predictionClass = "medium-risk";
    predictionIcon = "⚠";
    predictionText = "Low Risk";
  }

  // ==========================================
  // CCI RESULT
  // ==========================================

  const riskAnalysis = result.risk_analysis || {};

  const cci =
    riskAnalysis.cci_score ??
    riskAnalysis.cirs_score ??
    result.cci_score ??
    result.CCI_score ??
    result.cirs_score ??
    result.CIRS_score ??
    null;

  const cciRisk =
    riskAnalysis.cci_risk ??
    riskAnalysis.cirs_risk ??
    riskAnalysis.risk_level ??
    result.cci_risk ??
    result.cirs_risk ??
    result.overall_severity ??
    "Unavailable";

  // ==========================================
  // SHAP FEATURE DISPLAY
  // ==========================================

  const renderShapExplanation = (explanation) => {
    const features = Array.isArray(
      explanation?.shap_explanation
    )
      ? explanation.shap_explanation
      : [];

    if (features.length === 0) {
      return (
        <p className="empty-message">
          SHAP explanation is unavailable for this conflict.
        </p>
      );
    }

    return (
      <div className="conflict-shap">
        <h4>🔎 SHAP Explainability</h4>

        <p className="shap-description">
          These features explain how the model supports
          or opposes its predicted class. Values are model
          contribution values, not risk percentages.
        </p>

        <div className="shap-feature-list">
          {features.map((feature, index) => {
            const name =
              feature.feature ||
              feature.feature_name ||
              feature.name ||
              "Feature";

            const rawValue =
              feature.value ??
              feature.shap_value ??
              feature.contribution ??
              0;

            const value = Number(rawValue);

            const validValue = Number.isFinite(value)
              ? value
              : 0;

            const direction =
              feature.direction ||
              (validValue > 0
                ? "Supports the predicted class"
                : validValue < 0
                ? "Opposes the predicted class"
                : "No directional contribution");

            return (
              <div
                className="shap-feature"
                key={`${name}-${index}`}
              >
                <strong>{name}</strong>

                <span className="shap-value">
                  {validValue > 0 ? "+" : ""}
                  {validValue.toFixed(6)}
                </span>

                <p>{direction}</p>
              </div>
            );
          })}
        </div>
      </div>
    );
  };

  // ==========================================
  // RENDER
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

      {/* OVERALL SAFETY */}

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
                  <span>✓</span> {ingredient}
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
                  <span>✓</span> {ingredient}
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

      {/* CONFLICT RESULTS + INDIVIDUAL SHAP */}

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
              <strong>No Ingredient Conflicts Detected</strong>

              <p>
                No conflicting ingredient combinations were found
                between these two products.
              </p>
            </div>
          </div>
        ) : (
          <div className="conflict-list">

            {conflicts.map((conflict, index) => {
              const conflictSeverity = String(
                conflict.severity || "unknown"
              ).toLowerCase();

              const explanation =
                getConflictExplanation(conflict);

              return (
                <div
                  className={`conflict-item ${conflictSeverity}`}
                  key={index}
                >
                  <div className="conflict-icon">⚠️</div>

                  <div className="conflict-content">

                    <strong>
                      {conflict.ingredient_1 ||
                        conflict.ingredient1 ||
                        conflict.ingredient_a}
                      {" + "}
                      {conflict.ingredient_2 ||
                        conflict.ingredient2 ||
                        conflict.ingredient_b}
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

                    {/* XGBOOST RESULT FOR THIS CONFLICT */}

                    <div className="conflict-ml">
                      <h4>🤖 XGBoost Prediction</h4>

                      {explanation?.predicted_risk ? (
                        <p>
                          <strong>Predicted risk:</strong>{" "}
                          {explanation.predicted_risk}
                        </p>
                      ) : (
                        <p className="empty-message">
                          Prediction unavailable for this conflict.
                        </p>
                      )}

                      {explanation?.dataset_risk && (
                        <p>
                          <strong>Dataset risk:</strong>{" "}
                          {explanation.dataset_risk}
                        </p>
                      )}
                    </div>

                    {/* SHAP RESULT FOR THIS CONFLICT */}

                    {renderShapExplanation(explanation)}

                  </div>
                </div>
              );
            })}

          </div>
        )}
      </div>

      {/* CCI SCORE */}

      <div className="conflict-section">
        <h2>📊 Cosmetic Conflict Index (CCI)</h2>

        {cci !== null && Number.isFinite(Number(cci)) ? (
          <>
            <h3>{Number(cci).toFixed(2)} / 100</h3>

            <p>
              Risk category: {String(cciRisk)}
            </p>

            <progress
              value={Math.max(0, Math.min(100, Number(cci)))}
              max="100"
              aria-label="CCI score"
            />
          </>
        ) : (
          <p className="empty-message">
            CCI score is not available in the backend response yet.
          </p>
        )}
      </div>

      {/* SEVERITY DETAILS */}

      <div className="conflict-section">
        <h2>⚠️ Severity Assessment</h2>

        <p>
          <strong>Overall severity:</strong>{" "}
          {String(
            result.overall_severity ??
            result.dataset_severity ??
            result.safety_prediction ??
            result.prediction ??
            "Unavailable"
          )}
        </p>

        <p>
          <strong>Predicted risk:</strong>{" "}
          {String(
            result.predicted_risk ??
            result.predicted_severity ??
            "Unavailable"
          )}
        </p>
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
        <button onClick={() => navigate("/dashboard/analyze")}>
          Analyze Another
        </button>

        <button onClick={() => navigate("/dashboard/history")}>
          View History
        </button>
      </div>

    </div>
  );
}

export default Results;
