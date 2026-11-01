
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import traceback
import pytesseract

from engine.ingredient_matcher import match_ingredients
from engine.ocr_engine import extract_text, extract_ingredients
from engine.ingredient_cleaner import clean_ingredients
from engine.conflict_engine import ConflictEngine

from risk.risk_analyzer import (
    analyze_risk,
    analyze_what_if
)

# ==========================================
# TESSERACT OCR CONFIGURATION
# ==========================================

pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

# ==========================================
# FLASK APP
# ==========================================

app = Flask(__name__)
CORS(app)

# ==========================================
# PROJECT DIRECTORY
# ==========================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ==========================================
# UPLOAD FOLDER
# ==========================================

UPLOAD_FOLDER = os.path.join(
    BASE_DIR,
    "static",
    "uploads"
)

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# ==========================================
# CONFLICT ENGINE
# ==========================================

conflict_engine = ConflictEngine()

# ==========================================
# HOME / API HEALTH CHECK
# ==========================================

@app.route("/", methods=["GET"])
def home():

    return jsonify({
        "project": "Cosmetic Conflict Analyzer",
        "status": "Backend is running",
        "message": "Backend API is ready for frontend integration"
    })

# ==========================================
# ANALYZE TWO PRODUCTS
# ==========================================

@app.route("/api/analyze", methods=["POST"])
def analyze():

    try:

        # Check uploaded images

        if "image1" not in request.files:
            return jsonify({
                "success": False,
                "error": "Product 1 image is missing"
            }), 400

        if "image2" not in request.files:
            return jsonify({
                "success": False,
                "error": "Product 2 image is missing"
            }), 400

        image1 = request.files["image1"]
        image2 = request.files["image2"]

        if image1.filename == "":
            return jsonify({
                "success": False,
                "error": "Product 1 image was not selected"
            }), 400

        if image2.filename == "":
            return jsonify({
                "success": False,
                "error": "Product 2 image was not selected"
            }), 400

        # Save product images

        filepath1 = os.path.join(
            app.config["UPLOAD_FOLDER"],
            "product1.jpg"
        )

        filepath2 = os.path.join(
            app.config["UPLOAD_FOLDER"],
            "product2.jpg"
        )

        image1.save(filepath1)
        image2.save(filepath2)

        # ======================================
        # PRODUCT 1 OCR
        # ======================================

        print("\n========== PRODUCT 1 ==========")

        text1 = extract_text(filepath1)

        ingredients_text1 = extract_ingredients(text1)

        ingredients1 = clean_ingredients(
            ingredients_text1
        )

        matched_ingredients1 = match_ingredients(
            ingredients1
        )

        print("Product 1 ingredients:", ingredients1)

        # ======================================
        # PRODUCT 2 OCR
        # ======================================

        print("\n========== PRODUCT 2 ==========")

        text2 = extract_text(filepath2)

        ingredients_text2 = extract_ingredients(text2)

        ingredients2 = clean_ingredients(
            ingredients_text2
        )

        matched_ingredients2 = match_ingredients(
            ingredients2
        )

        print("Product 2 ingredients:", ingredients2)

        # ======================================
        # COMPARE PRODUCTS
        # ======================================

        print("\n========== CONFLICT ANALYSIS ==========")

        conflicts = conflict_engine.compare_products(
            ingredients1,
            ingredients2
        )

        print("Conflicts:", conflicts)

        # ======================================
        # OVERALL SEVERITY
        # ======================================

        overall_severity = (
            conflict_engine.calculate_overall_severity(
                conflicts
            )
        )

        print("Overall severity:", overall_severity)

        # ======================================
        # STATUS
        # ======================================

        status = conflict_engine.get_status(conflicts)

        # ======================================
        # CCI RISK ANALYSIS
        # ======================================

        all_ingredients = list(
            dict.fromkeys(ingredients1 + ingredients2)
        )

        risk_analysis = analyze_risk(
            all_ingredients,
            conflicts
        )

        print("CCI Score:", risk_analysis["cci_score"])
        print("Risk Level:", risk_analysis["risk_level"])

        # ======================================
        # RETURN JSON TO FRONTEND
        # ======================================

        return jsonify({

            "success": True,

            "product1": {
                "filename": image1.filename,
                "ingredients": ingredients1,
                "matched_ingredients": matched_ingredients1
            },

            "product2": {
                "filename": image2.filename,
                "ingredients": ingredients2,
                "matched_ingredients": matched_ingredients2
            },

            "ingredients": all_ingredients,

            "conflicts": conflicts,

            "overall_severity": overall_severity,

            "status": status,

            "risk_analysis": risk_analysis

        })

    except Exception as e:

        print("\n========== ANALYSIS ERROR ==========")

        traceback.print_exc()

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# ==========================================
# WHAT-IF ANALYSIS API
# ==========================================

@app.route("/api/what-if", methods=["POST"])
def what_if():

    try:

        data = request.get_json(silent=True)

        if not isinstance(data, dict):
            return jsonify({
                "success": False,
                "error": "Invalid JSON request."
            }), 400

        ingredients = data.get("ingredients")
        conflicts = data.get("conflicts")

        selected_ingredient_1 = data.get(
            "selected_ingredient_1"
        )

        selected_ingredient_2 = data.get(
            "selected_ingredient_2"
        )

        # Validate ingredients

        if not isinstance(ingredients, list):
            return jsonify({
                "success": False,
                "error": "A valid ingredients list is required."
            }), 400

        # Validate conflicts

        if not isinstance(conflicts, list):
            return jsonify({
                "success": False,
                "error": "A valid conflicts list is required."
            }), 400

        # Validate selected ingredients

        if (
            not isinstance(selected_ingredient_1, str)
            or not selected_ingredient_1.strip()
        ):
            return jsonify({
                "success": False,
                "error": "First selected ingredient is required."
            }), 400

        if (
            not isinstance(selected_ingredient_2, str)
            or not selected_ingredient_2.strip()
        ):
            return jsonify({
                "success": False,
                "error": "Second selected ingredient is required."
            }), 400

        print("\n========== WHAT-IF ANALYSIS ==========")

        print(
            "Selected pair:",
            selected_ingredient_1,
            "+",
            selected_ingredient_2
        )

        # Perform What-If analysis

        result = analyze_what_if(
            ingredients,
            conflicts,
            selected_ingredient_1,
            selected_ingredient_2
        )

        print("Original CCI:", result["original_cci"])
        print("Updated CCI:", result["updated_cci"])
        print("Original Risk:", result["original_risk"])
        print("Updated Risk:", result["updated_risk"])

        return jsonify({
            "success": True,
            "message": "What-If analysis completed successfully.",
            **result
        })

    except ValueError as e:

        return jsonify({
            "success": False,
            "error": str(e)
        }), 400

    except Exception as e:

        print("\n========== WHAT-IF ERROR ==========")

        traceback.print_exc()

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# ==========================================
# RUN APPLICATION
# ==========================================

if __name__ == "__main__":

    print("\n==========================================")
    print("COSMETIC CONFLICT ANALYZER")
    print("==========================================")

    print("Conflict dataset loaded successfully.")

    print("Tesseract OCR configured successfully.")

    print("Backend running at:")
    print("http://127.0.0.1:5000")

    print("\nAPI endpoints:")
    print("POST /api/analyze")
    print("POST /api/what-if")

    print("==========================================\n")

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )
