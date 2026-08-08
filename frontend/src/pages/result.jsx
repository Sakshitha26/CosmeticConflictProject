import { useLocation, useNavigate } from "react-router-dom";
import Navbar from "../components/navbar";
import Footer from "../components/footer";
import "./result.css";

function Result() {

    const navigate = useNavigate();
    const location = useLocation();

    const result = location.state || {
        overall_severity: "SAFE",
        reason: "No ingredient conflicts detected.",
        recommendation: "These two cosmetic products are safe to use together."
    };

    const getColor = () => {

        switch (result.overall_severity.toUpperCase()) {

            case "HIGH":
                return "#d32f2f";

            case "MEDIUM":
                return "#f9a825";

            default:
                return "#388e3c";

        }

    };

    const getEmoji = () => {

        switch (result.overall_severity.toUpperCase()) {

            case "HIGH":
                return "🔴";

            case "MEDIUM":
                return "🟡";

            default:
                return "🟢";

        }

    };

    return (

        <>

            <Navbar />

            <div className="result-container">

                <div className="result-card">

                    <h1>Analysis Result</h1>

                    <div
                        className="severity-box"
                        style={{ borderLeft: `8px solid ${getColor()}` }}
                    >

                        <h2>

                            {getEmoji()} {result.overall_severity} RISK

                        </h2>

                    </div>

                    <div className="result-section">

                        <h3>Reason</h3>

                        <p>{result.reason}</p>

                    </div>

                    <div className="result-section">

                        <h3>Recommendation</h3>

                        <p>{result.recommendation}</p>

                    </div>

                    <button
                        className="analyze-again"
                        onClick={() => navigate("/upload")}
                    >
                        Analyze Another Pair
                    </button>

                </div>

            </div>

            <Footer />

        </>

    );

}

export default Result;