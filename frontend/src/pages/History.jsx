import React from "react";
import { useNavigate } from "react-router-dom";
import "./History.css";

function History() {
  const navigate = useNavigate();

  const history =
    JSON.parse(localStorage.getItem("analysisHistory")) || [];

  const openResult = (item) => {
    sessionStorage.setItem(
      "latestAnalysis",
      JSON.stringify(item)
    );

    navigate("/dashboard/results");
  };

  return (
    <div className="history-page">

      <div className="history-heading">

        <div>
          <p>YOUR ACTIVITY</p>
          <h1>Analysis History</h1>
        </div>

        <button
          onClick={() => navigate("/dashboard/analyze")}
        >
          + New Analysis
        </button>

      </div>

      {history.length === 0 ? (

        <div className="empty-history">

          <div>🕘</div>

          <h2>No Analysis History</h2>

          <p>
            Your completed analyses will appear here.
          </p>

          <button
            onClick={() =>
              navigate("/dashboard/analyze")
            }
          >
            Start Your First Analysis
          </button>

        </div>

      ) : (

        <div className="history-list">

          {history.map((item, index) => (

            <div
              className="history-item"
              key={index}
            >

              <div className="history-icon">
                🧴
              </div>

              <div className="history-details">

                <h3>
                  Cosmetic Product Analysis
                </h3>

                <p>
                  {item.date}
                </p>

                <span>
                  Prediction:{" "}
                  <strong>
                    {item.safety_prediction ||
                      item.prediction ||
                      "Medium Risk"}
                  </strong>
                </span>

              </div>

              <button
                onClick={() => openResult(item)}
              >
                View Results →
              </button>

            </div>

          ))}

        </div>

      )}

    </div>
  );
}

export default History;