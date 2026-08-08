import { useState } from "react";
import { useNavigate } from "react-router-dom";
import Navbar from "../components/navbar";
import Footer from "../components/footer";
import { analyzeProducts } from "../services/api";
import "./upload.css";

function Upload() {

    const navigate = useNavigate();

    const [product1, setProduct1] = useState(null);
    const [product2, setProduct2] = useState(null);

    const [preview1, setPreview1] = useState("");
    const [preview2, setPreview2] = useState("");

    const [loading, setLoading] = useState(false);

    const handleProduct1 = (e) => {

        const file = e.target.files[0];

        if (file) {
            setProduct1(file);
            setPreview1(URL.createObjectURL(file));
        }

    };

    const handleProduct2 = (e) => {

        const file = e.target.files[0];

        if (file) {
            setProduct2(file);
            setPreview2(URL.createObjectURL(file));
        }

    };

    const handleAnalyze = async () => {

        if (!product1 || !product2) {
            alert("Please upload both product images.");
            return;
        }

        try {

            setLoading(true);

            const result = await analyzeProducts(product1, product2);

            navigate("/result", {
                state: result
            });

        } catch (error) {

            console.error(error);

            alert("Analysis failed.");

        } finally {

            setLoading(false);

        }

    };

    return (

        <>

            <Navbar />

            <div className="upload-container">

                <h1>Upload Cosmetic Products</h1>

                <p>
                    Upload the ingredient label images of two cosmetic
                    products to check whether they are safe to use together.
                </p>

                <div className="upload-grid">

                    <div className="upload-card">

                        <h2>Product 1</h2>

                        <input
                            type="file"
                            accept="image/*"
                            onChange={handleProduct1}
                        />

                        {preview1 && (
                            <img
                                src={preview1}
                                alt="Product 1"
                                className="preview-image"
                            />
                        )}

                    </div>

                    <div className="upload-card">

                        <h2>Product 2</h2>

                        <input
                            type="file"
                            accept="image/*"
                            onChange={handleProduct2}
                        />

                        {preview2 && (
                            <img
                                src={preview2}
                                alt="Product 2"
                                className="preview-image"
                            />
                        )}

                    </div>

                </div>

                <button
                    className="analyze-btn"
                    onClick={handleAnalyze}
                    disabled={loading}
                >
                    {loading ? "Analyzing..." : "Analyze Compatibility"}
                </button>

            </div>

            <Footer />

        </>

    );

}

export default Upload;