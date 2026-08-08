import { useNavigate } from "react-router-dom";
import Navbar from "../components/navbar";
import Footer from "../components/footer";
import "./home.css";

function Home() {

    const navigate = useNavigate();

    return (
        <>

            <Navbar />

            <div className="home-container">

                <div className="hero-section">

                    <h1>🧴 Cosmetic Conflict Analyzer</h1>

                    <p>
                        Check whether two cosmetic products are safe to use
                        together by uploading their ingredient label images.
                    </p>

                    <button
                        className="start-btn"
                        onClick={() => navigate("/upload")}
                    >
                        Start Analysis
                    </button>

                </div>

                <div className="about-section">

                    <h2>How It Works</h2>

                    <div className="steps">

                        <div className="step-card">

                            <h3>1️⃣ Login</h3>

                            <p>
                                Login or register to access the Cosmetic
                                Conflict Analyzer.
                            </p>

                        </div>

                        <div className="step-card">

                            <h3>2️⃣ Upload Images</h3>

                            <p>
                                Upload ingredient label images of two cosmetic
                                products.
                            </p>

                        </div>

                        <div className="step-card">

                            <h3>3️⃣ AI Analysis</h3>

                            <p>
                                The backend extracts ingredients using OCR,
                                cleans the ingredient names, and checks them
                                against the conflict dataset.
                            </p>

                        </div>

                        <div className="step-card">

                            <h3>4️⃣ View Result</h3>

                            <p>
                                You will only see the overall compatibility
                                result:
                            </p>

                            <ul>
                                <li>🔴 High Risk</li>
                                <li>🟡 Medium Risk</li>
                                <li>🟢 Safe</li>
                            </ul>

                        </div>

                    </div>

                </div>

            </div>

            <Footer />

        </>
    );
}

export default Home;