import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { analyzeProducts } from "../services/api";
import "./Analyze.css";

function Analyze() {
  const navigate = useNavigate();

  const [image1, setImage1] = useState(null);
  const [image2, setImage2] = useState(null);

  const [preview1, setPreview1] = useState(null);
  const [preview2, setPreview2] = useState(null);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleImage1 = (e) => {
    const file = e.target.files[0];

    if (!file) return;

    setImage1(file);
    setPreview1(URL.createObjectURL(file));
    setError("");
  };

  const handleImage2 = (e) => {
    const file = e.target.files[0];

    if (!file) return;

    setImage2(file);
    setPreview2(URL.createObjectURL(file));
    setError("");
  };

  const handleAnalyze = async () => {

    if (!image1 || !image2) {
      setError("Please upload both product ingredient images.");
      return;
    }

    try {

      setLoading(true);
      setError("");

      const result = await analyzeProducts(
        image1,
        image2
      );

      sessionStorage.setItem(
        "latestAnalysis",
        JSON.stringify(result)
      );

      const history =
        JSON.parse(localStorage.getItem("analysisHistory")) || [];

      history.unshift({
        ...result,
        date: new Date().toLocaleString()
      });

      localStorage.setItem(
        "analysisHistory",
        JSON.stringify(history)
      );

      navigate("/dashboard/results");

    } catch (err) {

      console.error(err);

      setError(
        "Unable to analyze the products. Please check whether the backend is running."
      );

    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="analyze-page">

      <div className="analyze-heading">
        <p>PRODUCT ANALYSIS</p>

        <h1>Analyze Cosmetic Ingredients</h1>

        <span>
          Upload ingredient images from two products to detect
          conflicts and predict safety.
        </span>
      </div>

      <div className="upload-container">

        <div className="upload-box">

          <div className="upload-icon">
            📷
          </div>

          <h3>Product 1</h3>

          <p>
            Upload ingredient label image
          </p>

          <input
            id="image1"
            type="file"
            accept="image/*"
            onChange={handleImage1}
          />

          <label htmlFor="image1">
            Choose Image
          </label>

          {preview1 && (
            <img
              src={preview1}
              alt="Product 1 preview"
              className="image-preview"
            />
          )}

          {image1 && (
            <p className="file-name">
              {image1.name}
            </p>
          )}

        </div>

        <div className="compare-symbol">
          +
        </div>

        <div className="upload-box">

          <div className="upload-icon">
            📷
          </div>

          <h3>Product 2</h3>

          <p>
            Upload ingredient label image
          </p>

          <input
            id="image2"
            type="file"
            accept="image/*"
            onChange={handleImage2}
          />

          <label htmlFor="image2">
            Choose Image
          </label>

          {preview2 && (
            <img
              src={preview2}
              alt="Product 2 preview"
              className="image-preview"
            />
          )}

          {image2 && (
            <p className="file-name">
              {image2.name}
            </p>
          )}

        </div>

      </div>

      {error && (
        <div className="analyze-error">
          {error}
        </div>
      )}

      <div className="analyze-action">

        <button
          onClick={handleAnalyze}
          disabled={loading}
        >
          {loading
            ? "Analyzing..."
            : "Analyze Products →"}
        </button>

      </div>

      <div className="analysis-process">

        <div>
          <span>1</span>
          <p>Upload Images</p>
        </div>

        <div>
          <span>2</span>
          <p>OCR Extraction</p>
        </div>

        <div>
          <span>3</span>
          <p>Conflict Detection</p>
        </div>

        <div>
          <span>4</span>
          <p>Safety Prediction</p>
        </div>

      </div>

    </div>
  );
}

export default Analyze;