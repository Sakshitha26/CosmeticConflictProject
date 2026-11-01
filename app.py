
from flask import Flask, request, jsonify
from flask_cors import CORS

import os
import traceback
import math

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
# XGBOOST + SHAP
# ==========================================

ML_AVAILABLE = False
ml_predictor = None

try:

    import ml.predict as ml_predictor

    ML_AVAILABLE = True

    print("XGBoost ML predictor loaded successfully.")
    print("SHAP explanation module available.")

except Exception as e:

    print("XGBoost ML predictor could not be loaded.")
    print("ML error:", str(e))

    traceback.print_exc()


# ==========================================
# JSON CONVERSION HELPER
# ==========================================

def make_json_safe(value):

    if isinstance(value, dict):

        return {
            str(key): make_json_safe(val)
            for key, val in value.items()
        }

    if isinstance(value, (list, tuple)):

        return [
            make_json_safe(item)
            for item in value
        ]

    if hasattr(value, "item"):

        try:
            return make_json_safe(value.item())
        except Exception:
            pass

    if isinstance(value, float):

        if not math.isfinite(value):
            return None

    return value


# ==========================================
# REMOVE DUPLICATE INGREDIENTS
# ==========================================

def unique_ingredients(ingredients):

    result = []
    seen = set()

    for ingredient in ingredients:

        ingredient = str(ingredient).strip()

        key = ingredient.lower()

        if key and key not in seen:

            seen.add(key)

            result.append(ingredient)

    return result


# ==========================================
# EXTRACT INGREDIENT PAIR FROM A CONFLICT
# ==========================================

def get_conflict_ingredients(conflict):

    """
    Extracts the two ingredients from a conflict.

    Supports common conflict dictionary key formats.
    """

    if not isinstance(conflict, dict):
        return None, None

    ingredient_1 = (
        conflict.get("ingredient_1")
        or conflict.get("ingredient1")
        or conflict.get("ingredient_a")
        or conflict.get("ingredientA")
    )

    ingredient_2 = (
        conflict.get("ingredient_2")
        or conflict.get("ingredient2")
        or conflict.get("ingredient_b")
        or conflict.get("ingredientB")
    )

    # Support conflicts containing an ingredients list.

    if not ingredient_1 or not ingredient_2:

        ingredients = conflict.get("ingredients")

        if isinstance(ingredients, (list, tuple)) and len(ingredients) >= 2:

            ingredient_1 = ingredient_1 or ingredients[0]
            ingredient_2 = ingredient_2 or ingredients[1]

    if not ingredient_1 or not ingredient_2:

        return None, None

    return (
        str(ingredient_1).strip(),
        str(ingredient_2).strip()
    )


# ==========================================
# ANALYZE DETECTED CONFLICTS USING XGBOOST
# AND SHAP
# ==========================================

def analyze_conflict_explanations(conflicts):

    """
    Runs XGBoost and SHAP ONLY for conflicts
    already detected by the Conflict Engine.

    It does not analyze every cross-product pair.

    Each detected conflict receives its own
    prediction and SHAP explanation.
    """

    conflict_explanations = []

    result = {

        "available": ML_AVAILABLE,

        "status": "Not available",

        "conflicts_analyzed": 0,

        "conflict_explanations": conflict_explanations,

        "errors": []

    }

    if not ML_AVAILABLE or ml_predictor is None:

        result["status"] = "XGBoost predictor unavailable"

        return result

    if not conflicts:

        result["status"] = "No detected conflicts to explain"

        return result

    print("\n==========================================")
    print("DETECTED CONFLICT XGBOOST + SHAP ANALYSIS")
    print("==========================================")

    for conflict_index, conflict in enumerate(conflicts):

        ingredient_1, ingredient_2 = (
            get_conflict_ingredients(conflict)
        )

        if not ingredient_1 or not ingredient_2:

            print(
                "Could not extract ingredient pair from conflict:",
                conflict
            )

            result["errors"].append({

                "conflict_index": conflict_index,

                "error": (
                    "Could not identify the two ingredients "
                    "in this conflict."
                )

            })

            continue

        try:

            print(
                f"\nAnalyzing conflict: "
                f"{ingredient_1} + {ingredient_2}"
            )

            # ----------------------------------
            # DATASET LOOKUP
            # ----------------------------------

            pair_info = ml_predictor.find_pair(
                ingredient_1,
                ingredient_2
            )

            co_occurrence = pair_info.get(
                "co_occurrence",
                0
            )

            # ----------------------------------
            # XGBOOST PREDICTION
            # ----------------------------------

            (
                predicted_risk,
                probabilities,
                X,
                predicted_class,
                external_co_occurrence
            ) = ml_predictor.predict_risk(

                ingredient_1,

                ingredient_2,

                co_occurrence

            )

            # ----------------------------------
            # SHAP EXPLANATION
            # ----------------------------------

            shap_values = ml_predictor.explain_prediction(
                X
            )

            shap_explanation = (
                ml_predictor.get_shap_explanations(

                    shap_values,

                    predicted_class,

                    X=X,

                    top_n=5

                )
            )

            # ----------------------------------
            # CONFLICT-SPECIFIC RESULT
            # ----------------------------------

            conflict_result = {

                "conflict_index": conflict_index,

                "ingredient_1": ingredient_1,

                "ingredient_2": ingredient_2,

                "predicted_risk": predicted_risk,

                "shap_explanation": shap_explanation,

                "dataset_pair_found": pair_info.get(
                    "found",
                    False
                ),

                "dataset_risk": pair_info.get(
                    "dataset_risk"
                ),

                "severity_explanation": pair_info.get(
                    "severity_note",
                    ""
                ),

                "external_co_occurrence": (
                    external_co_occurrence
                )

            }

            conflict_explanations.append(
                conflict_result
            )

            print(
                "Predicted risk:",
                predicted_risk
            )

            print(
                "SHAP features:",
                len(shap_explanation)
            )

        except Exception as conflict_error:

            print(
                "Conflict ML analysis failed:",
                ingredient_1,
                "+",
                ingredient_2
            )

            print(str(conflict_error))

            result["errors"].append({

                "ingredient_1": ingredient_1,

                "ingredient_2": ingredient_2,

                "error": str(conflict_error)

            })

            # Keep the detected conflict in the response
            # even if its ML explanation fails.

            conflict_explanations.append({

                "conflict_index": conflict_index,

                "ingredient_1": ingredient_1,

                "ingredient_2": ingredient_2,

                "predicted_risk": "Unavailable",

                "shap_explanation": [],

                "dataset_pair_found": False,

                "dataset_risk": None,

                "severity_explanation": "",

                "external_co_occurrence": 0.0

            })

    # --------------------------------------
    # FINAL RESULT
    # --------------------------------------

    result["conflicts_analyzed"] = len(
        conflict_explanations
    )

    result["conflict_explanations"] = (
        conflict_explanations
    )

    if conflict_explanations:

        result["status"] = (
            "Detected conflict XGBoost and SHAP analysis completed"
        )

    else:

        result["status"] = (
            "No conflict explanations could be generated"
        )

    print("\n==========================================")
    print("CONFLICT SHAP ANALYSIS COMPLETED")
    print("==========================================")

    print(
        "Detected conflicts analyzed:",
        result["conflicts_analyzed"]
    )

    return result


# ==========================================
# HOME / API HEALTH CHECK
# ==========================================

@app.route("/", methods=["GET"])
def home():

    return jsonify({

        "project": (
            "Real-Time Cosmetic Conflict Detection "
            "and Safety Auditing System"
        ),

        "status": "Backend is running",

        "modules": {

            "ocr": True,

            "conflict_engine": True,

            "cci_risk_analysis": True,

            "xgboost": ML_AVAILABLE,

            "shap": ML_AVAILABLE

        },

        "message": (
            "Backend API is ready for frontend integration"
        )

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

                "error": (
                    "Product 1 image was not selected"
                )

            }), 400

        if image2.filename == "":

            return jsonify({

                "success": False,

                "error": (
                    "Product 2 image was not selected"
                )

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

        ingredients_text1 = extract_ingredients(
            text1
        )

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

        ingredients_text2 = extract_ingredients(
            text2
        )

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
        print(risk_analysis["cci_score"])

        print("Risk Level:")
        print(risk_analysis["risk_level"])

        print("Conflict Count:")
        print(risk_analysis["conflict_count"])

        print("Cumulative Risk:")
        print(risk_analysis["cumulative_risk"])

        print("Conflict Density:")
        print(risk_analysis["conflict_density"])

        print("Recommendation:")
        print(risk_analysis["recommendation"])

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
        # XGBOOST + SHAP FOR DETECTED CONFLICTS
        # ======================================

        conflict_ml_result = analyze_conflict_explanations(
            conflicts
        )

        # ======================================
        # JSON-SAFE CONVERSION
        # ======================================

        conflicts = make_json_safe(
            conflicts
        )

        risk_analysis = make_json_safe(
            risk_analysis
        )

        conflict_ml_result = make_json_safe(
            conflict_ml_result
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

                "ingredients": make_json_safe(
                    ingredients1
                ),

                "matched_ingredients": make_json_safe(
                    matched_ingredients1
                )

            },

            # ----------------------------------
            # PRODUCT 2
            # ----------------------------------

            "product2": {

                "filename": image2.filename,

                "ingredients": make_json_safe(
                    ingredients2
                ),

                "matched_ingredients": make_json_safe(
                    matched_ingredients2
                )

            },

            # ----------------------------------
            # CONFLICT RESULTS
            # ----------------------------------

            "conflicts": conflicts,

            # ----------------------------------
            # EXISTING CONFLICT SEVERITY
            # ----------------------------------

            "overall_severity": overall_severity,

            "status": status,

            # ----------------------------------
            # CCI / RISK RESULTS
            # ----------------------------------

            "risk_analysis": {

                "cci_score": risk_analysis["cci_score"],

                "risk_level": risk_analysis["risk_level"],

                "conflict_count": risk_analysis["conflict_count"],

                "cumulative_risk": risk_analysis["cumulative_risk"],

                "conflict_density": risk_analysis["conflict_density"],

                "recommendation": risk_analysis["recommendation"]

            },

            # ----------------------------------
            # MACHINE LEARNING SUMMARY
            # ----------------------------------

            "machine_learning": {

                "available": conflict_ml_result["available"],

                "status": conflict_ml_result["status"],

                "conflicts_analyzed": (
                    conflict_ml_result["conflicts_analyzed"]
                )

            },

            # ----------------------------------
            # SHAP FOR DETECTED CONFLICTS ONLY
            # ----------------------------------

            "conflict_explanations": (
                conflict_ml_result["conflict_explanations"]
            ),

            # ----------------------------------
            # ML ERRORS
            # ----------------------------------

            "ml_errors": conflict_ml_result["errors"]

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

    print(
        "SHAP:",
        "AVAILABLE" if ML_AVAILABLE else "NOT AVAILABLE"
    )

    print("\nBackend running at:")

    print("http://127.0.0.1:5000")

    print("\nAPI endpoint:")

    print("POST /api/analyze")

    print("==========================================\n")

    app.run(

        debug=True,

        host="127.0.0.1",

        port=5000

    )
