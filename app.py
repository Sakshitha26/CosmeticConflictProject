from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import traceback

from engine.ingredient_matcher import match_ingredients
from engine.ocr_engine import extract_text, extract_ingredients
from engine.ingredient_cleaner import clean_ingredients
from engine.conflict_engine import ConflictEngine


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

os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)

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

        # --------------------------------------
        # CHECK PRODUCT 1
        # --------------------------------------

        if "image1" not in request.files:

            return jsonify({
                "success": False,
                "error": "Product 1 image is missing"
            }), 400


        # --------------------------------------
        # CHECK PRODUCT 2
        # --------------------------------------

        if "image2" not in request.files:

            return jsonify({
                "success": False,
                "error": "Product 2 image is missing"
            }), 400


        image1 = request.files["image1"]
        image2 = request.files["image2"]


        # --------------------------------------
        # CHECK FILENAMES
        # --------------------------------------

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


        # ======================================
        # SAVE PRODUCT IMAGES
        # ======================================

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

        print("\n==========================================")
        print("PRODUCT 1")
        print("==========================================")

        text1 = extract_text(filepath1)

        ingredients_text1 = extract_ingredients(text1)

        ingredients1 = clean_ingredients(
            ingredients_text1
        )

        matched_ingredients1 = match_ingredients(
            ingredients1
        )

        print("Product 1 ingredients:")
        print(ingredients1)

        print("Product 1 matched ingredients:")
        print(matched_ingredients1)


        # ======================================
        # PRODUCT 2 OCR
        # ======================================

        print("\n==========================================")
        print("PRODUCT 2")
        print("==========================================")

        text2 = extract_text(filepath2)

        ingredients_text2 = extract_ingredients(text2)

        ingredients2 = clean_ingredients(
            ingredients_text2
        )

        matched_ingredients2 = match_ingredients(
            ingredients2
        )

        print("Product 2 ingredients:")
        print(ingredients2)

        print("Product 2 matched ingredients:")
        print(matched_ingredients2)


        # ======================================
        # COMPARE PRODUCTS
        # ======================================

        print("\n==========================================")
        print("CONFLICT ANALYSIS")
        print("==========================================")

        conflicts = conflict_engine.compare_products(
            ingredients1,
            ingredients2
        )

        print("Conflicts:")
        print(conflicts)


        # ======================================
        # OVERALL SEVERITY
        # ======================================

        overall_severity = (
            conflict_engine.calculate_overall_severity(
                conflicts
            )
        )

        print("Overall severity:")
        print(overall_severity)


        # ======================================
        # STATUS
        # ======================================

        try:

            status = conflict_engine.get_status(
                conflicts
            )

        except AttributeError:

            if overall_severity == "high":

                status = "WARNING"

            elif overall_severity == "medium":

                status = "CAUTION"

            elif overall_severity == "low":

                status = "LOW RISK"

            else:

                status = "SAFE"


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

            "conflicts": conflicts,

            "overall_severity": overall_severity,

            "status": status

        })


    # ======================================
    # ERROR HANDLING
    # ======================================

    except Exception as e:

        print("\n==========================================")
        print("ERROR")
        print("==========================================")

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

    print("Backend running at:")
    print("http://127.0.0.1:5000")

    print("\nAPI endpoint:")
    print("POST /api/analyze")

    print("==========================================\n")

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )