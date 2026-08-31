from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import traceback

from engine.ingredient_matcher import match_ingredients
from engine.ocr_engine import extract_text, extract_ingredients
from engine.ingredient_cleaner import clean_ingredients
from engine.conflict_engine import ConflictEngine

from risk.risk_analyzer import analyze_risk


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
# XGBOOST ML
# ==========================================

ML_AVAILABLE = False
predict_risk = None

try:

    from ml.predict import predict_risk

    ML_AVAILABLE = True

    print("XGBoost ML predictor loaded successfully.")

except Exception as e:

    print("XGBoost ML predictor could not be loaded.")
    print("ML error:", e)


# ==========================================
# HOME / API HEALTH CHECK
# ==========================================

@app.route("/", methods=["GET"])
def home():

    return jsonify({

        "project": "Real-Time Cosmetic Conflict Detection and Safety Auditing System",

        "status": "Backend is running",

        "modules": {

            "ocr": True,

            "conflict_engine": True,

            "cci_risk_analysis": True,

            "xgboost": ML_AVAILABLE,

            "shap": ML_AVAILABLE

        },

        "message": "Backend API is ready for frontend integration"

    })


# ==========================================
# ANALYZE TWO PRODUCTS
# ==========================================

@app.route("/api/analyze", methods=["POST"])
def analyze():

    try:

        # ======================================
        # CHECK PRODUCT 1
        # ======================================

        if "image1" not in request.files:

            return jsonify({

                "success": False,

                "error": "Product 1 image is missing"

            }), 400


        # ======================================
        # CHECK PRODUCT 2
        # ======================================

        if "image2" not in request.files:

            return jsonify({

                "success": False,

                "error": "Product 2 image is missing"

            }), 400


        image1 = request.files["image1"]
        image2 = request.files["image2"]


        # ======================================
        # CHECK FILENAMES
        # ======================================

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
        print("PRODUCT 1 OCR")
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
        print("PRODUCT 2 OCR")
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
        # COMBINE INGREDIENTS
        # ======================================

        all_ingredients = (
            ingredients1 + ingredients2
        )


        # ======================================
        # CONFLICT ANALYSIS
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

        print("\n==========================================")
        print("OVERALL SEVERITY")
        print("==========================================")

        overall_severity = (

            conflict_engine.calculate_overall_severity(

                conflicts

            )

        )

        print("Overall severity:")
        print(overall_severity)


        # ======================================
        # CCI + RISK ANALYSIS
        # ======================================

        print("\n==========================================")
        print("CCI + RISK ANALYSIS")
        print("==========================================")

        risk_analysis = analyze_risk(

            all_ingredients,

            conflicts

        )


        print("CCI Score:")
        print(
            risk_analysis["cci_score"]
        )

        print("Risk Level:")
        print(
            risk_analysis["risk_level"]
        )

        print("Conflict Count:")
        print(
            risk_analysis["conflict_count"]
        )

        print("Cumulative Risk:")
        print(
            risk_analysis["cumulative_risk"]
        )

        print("Conflict Density:")
        print(
            risk_analysis["conflict_density"]
        )

        print("Recommendation:")
        print(
            risk_analysis["recommendation"]
        )


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
        # ML INFORMATION
        # ======================================

        ml_result = {

            "available": ML_AVAILABLE

        }


        # ======================================
        # OPTIONAL XGBOOST PREDICTION
        # ======================================
        #
        # The conflict engine + CCI remain the
        # primary product-level analysis.
        #
        # XGBoost is included separately so
        # ML does not replace the existing
        # conflict detection logic.
        #
        # ======================================

        if ML_AVAILABLE:

            try:

                ml_result["status"] = "XGBoost model loaded"

            except Exception as ml_error:

                ml_result["status"] = "XGBoost unavailable"

                ml_result["error"] = str(
                    ml_error
                )


        # ======================================
        # RETURN RESULT TO FRONTEND
        # ======================================

        return jsonify({

            "success": True,


            # ----------------------------------
            # PRODUCT 1
            # ----------------------------------

            "product1": {

                "filename": image1.filename,

                "ingredients": ingredients1,

                "matched_ingredients":
                    matched_ingredients1

            },


            # ----------------------------------
            # PRODUCT 2
            # ----------------------------------

            "product2": {

                "filename": image2.filename,

                "ingredients": ingredients2,

                "matched_ingredients":
                    matched_ingredients2

            },


            # ----------------------------------
            # CONFLICT RESULTS
            # ----------------------------------

            "conflicts": conflicts,


            # ----------------------------------
            # EXISTING CONFLICT SEVERITY
            # ----------------------------------

            "overall_severity":
                overall_severity,

            "status":
                status,


            # ----------------------------------
            # CCI / RISK RESULTS
            # ----------------------------------

            "risk_analysis": {

                "cci_score":
                    risk_analysis["cci_score"],

                "risk_level":
                    risk_analysis["risk_level"],

                "conflict_count":
                    risk_analysis["conflict_count"],

                "cumulative_risk":
                    risk_analysis["cumulative_risk"],

                "conflict_density":
                    risk_analysis["conflict_density"],

                "recommendation":
                    risk_analysis["recommendation"]

            },


            # ----------------------------------
            # MACHINE LEARNING
            # ----------------------------------

            "machine_learning": ml_result

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
    print("REAL-TIME COSMETIC CONFLICT ANALYZER")
    print("==========================================")

    print("Conflict Engine: AVAILABLE")

    print("CCI Risk Analysis: AVAILABLE")

    print(
        "XGBoost ML:",
        "AVAILABLE" if ML_AVAILABLE else "NOT AVAILABLE"
    )

    print("\nBackend running at:")

    print(
        "http://127.0.0.1:5000"
    )

    print("\nAPI endpoint:")

    print(
        "POST /api/analyze"
    )

    print("==========================================\n")


    app.run(

        debug=True,

        host="127.0.0.1",

        port=5000

    )