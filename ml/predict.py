
import os
import pickle
import re
import warnings

import numpy as np
import pandas as pd
import xgboost as xgb

from xgboost import XGBClassifier

warnings.filterwarnings("ignore")


# ============================================================
# 1. PATHS
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

DATA_PATH = os.path.join(
    BASE_DIR,
    "data",
    "combined_ingredient_pairs2.xlsx"
)

MODEL_DIR = os.path.join(
    BASE_DIR,
    "ml",
    "model"
)

MODEL_PATH = os.path.join(
    MODEL_DIR,
    "xgboost_risk_model.json"
)

VECTORIZER_PATH = os.path.join(
    MODEL_DIR,
    "tfidf_vectorizer.pkl"
)

RISK_CLASSES_PATH = os.path.join(
    MODEL_DIR,
    "risk_classes.npy"
)

FEATURE_NAMES_PATH = os.path.join(
    MODEL_DIR,
    "feature_names.npy"
)


# ============================================================
# 2. RISK CLASSES
# ============================================================

RISK_CLASSES = [
    "Safe",
    "Medium Risk",
    "High Risk"
]


# ============================================================
# 3. CIRS - COSMETIC INTERACTION RISK SCORE
# ============================================================

def calculate_cirs(
    severity_score,
    co_occurrence_score,
    external_evidence_score,
    interaction_score
):

    cirs = (
        0.40 * severity_score
        + 0.25 * co_occurrence_score
        + 0.20 * external_evidence_score
        + 0.15 * interaction_score
    )

    return max(
        0,
        min(100, cirs)
    )


def classify_cirs(cirs):

    if cirs <= 30:
        return "Safe"

    elif cirs <= 60:
        return "Medium Risk"

    else:
        return "High Risk"


# ============================================================
# 4. CLEAN INGREDIENT
# ============================================================

def clean_ingredient(value):

    value = str(value).lower().strip()

    value = value.replace("-", " ")
    value = value.replace("_", " ")

    value = re.sub(
        r"[^a-z0-9\s]",
        " ",
        value
    )

    value = re.sub(
        r"\s+",
        " ",
        value
    )

    return value.strip()


# ============================================================
# 5. LOAD DATASET
# ============================================================

print("\n========================================")
print("LOADING PREDICTION DATA")
print("========================================")

if not os.path.exists(DATA_PATH):

    raise FileNotFoundError(
        f"Dataset not found:\n{DATA_PATH}"
    )

df = pd.read_excel(DATA_PATH)

required_columns = [
    "Ingredient_A",
    "Ingredient_B",
    "Severity"
]

missing_columns = [
    column
    for column in required_columns
    if column not in df.columns
]

if missing_columns:

    raise ValueError(
        f"Missing required columns: {missing_columns}\n"
        f"Available columns: {df.columns.tolist()}"
    )


if "Co_Occurrence_Count" not in df.columns:

    df["Co_Occurrence_Count"] = 0.0


df["Ingredient_A"] = (
    df["Ingredient_A"].apply(clean_ingredient)
)

df["Ingredient_B"] = (
    df["Ingredient_B"].apply(clean_ingredient)
)


df["Co_Occurrence_Count"] = pd.to_numeric(
    df["Co_Occurrence_Count"],
    errors="coerce"
).fillna(0)


df["Severity"] = (
    df["Severity"]
    .astype(str)
    .str.lower()
    .str.strip()
)


print("Prediction dataset loaded successfully!")
print("Rows:", len(df))
print("Columns:", df.columns.tolist())


# ============================================================
# 6. LOAD XGBOOST MODEL
# ============================================================

print("\n========================================")
print("LOADING XGBOOST MODEL")
print("========================================")

if not os.path.exists(MODEL_PATH):

    raise FileNotFoundError(
        f"XGBoost model not found:\n{MODEL_PATH}"
    )

model = XGBClassifier(
    objective="multi:softprob",
    num_class=3
)

model.load_model(MODEL_PATH)

print("XGBoost model loaded successfully!")


# ============================================================
# 7. LOAD TF-IDF VECTORIZER
# ============================================================

print("\n========================================")
print("LOADING TF-IDF VECTORIZER")
print("========================================")

if not os.path.exists(VECTORIZER_PATH):

    raise FileNotFoundError(
        f"TF-IDF vectorizer not found:\n{VECTORIZER_PATH}"
    )

with open(VECTORIZER_PATH, "rb") as f:

    vectorizer = pickle.load(f)

print("TF-IDF vectorizer loaded successfully!")


# ============================================================
# 8. LOAD RISK CLASSES
# ============================================================

if os.path.exists(RISK_CLASSES_PATH):

    loaded_classes = np.load(
        RISK_CLASSES_PATH,
        allow_pickle=True
    )

    if len(loaded_classes) == 3:

        RISK_CLASSES = [
            str(x)
            for x in loaded_classes
        ]


# ============================================================
# 9. LOAD FEATURE NAMES
# ============================================================

feature_names = None

if os.path.exists(FEATURE_NAMES_PATH):

    feature_names = np.load(
        FEATURE_NAMES_PATH,
        allow_pickle=True
    )


# ============================================================
# 10. LOAD EXTERNAL EVIDENCE
# ============================================================

print("\n========================================")
print("LOADING EXTERNAL EVIDENCE")
print("========================================")

try:

    from .external_evidence import (
        load_external_evidence,
        get_external_co_occurrence
    )

    external_df = load_external_evidence()

    EXTERNAL_EVIDENCE_AVAILABLE = True

    print("External evidence loaded successfully!")

except Exception as e:

    print("External evidence could not be loaded.")
    print("Error:", str(e))

    external_df = None

    EXTERNAL_EVIDENCE_AVAILABLE = False


# ============================================================
# 11. CREATE MODEL TEXT
# ============================================================

def create_model_text(
    ingredient_1,
    ingredient_2
):

    ingredient_1 = clean_ingredient(ingredient_1)
    ingredient_2 = clean_ingredient(ingredient_2)

    token_1 = ingredient_1.replace(" ", "_")
    token_2 = ingredient_2.replace(" ", "_")

    canonical_pair = "||".join(
        sorted([
            ingredient_1,
            ingredient_2
        ])
    )

    pair_token = (
        canonical_pair
        .replace("||", "__")
        .replace(" ", "_")
    )

    ingredient_text = (
        "ING1_"
        + token_1
        + " "
        + "ING2_"
        + token_2
    )

    pair_text = "PAIR_" + pair_token

    return ingredient_text + " " + pair_text


# ============================================================
# 12. CREATE CANONICAL PAIR
# ============================================================

def create_canonical_pair(
    ingredient_1,
    ingredient_2
):

    ingredient_1 = clean_ingredient(ingredient_1)
    ingredient_2 = clean_ingredient(ingredient_2)

    return "||".join(
        sorted([
            ingredient_1,
            ingredient_2
        ])
    )


# ============================================================
# 13. FIND PAIR IN DATASET
# ============================================================

def find_pair(
    ingredient_1,
    ingredient_2
):

    ingredient_1 = clean_ingredient(ingredient_1)
    ingredient_2 = clean_ingredient(ingredient_2)

    direct = df[
        (df["Ingredient_A"] == ingredient_1)
        &
        (df["Ingredient_B"] == ingredient_2)
    ]

    reverse = df[
        (df["Ingredient_A"] == ingredient_2)
        &
        (df["Ingredient_B"] == ingredient_1)
    ]

    if len(direct) > 0:

        row = direct.iloc[0]

    elif len(reverse) > 0:

        row = reverse.iloc[0]

    else:

        return {
            "found": False,
            "co_occurrence": 0.0,
            "dataset_risk": None,
            "severity_note": ""
        }

    severity_note = ""

    explanation_column = None

    if "Severity_Explanation" in df.columns:

        explanation_column = "Severity_Explanation"

    elif "Severity Explanation" in df.columns:

        explanation_column = "Severity Explanation"

    if explanation_column is not None:

        if pd.notna(row[explanation_column]):

            severity_note = str(
                row[explanation_column]
            )

    return {

        "found": True,

        "co_occurrence": float(
            row["Co_Occurrence_Count"]
        ),

        "dataset_risk": str(
            row["Severity"]
        ).title(),

        "severity_note": severity_note

    }


# ============================================================
# 14. GET EXTERNAL CO-OCCURRENCE
# ============================================================

def get_external_value(
    ingredient_1,
    ingredient_2
):

    if not EXTERNAL_EVIDENCE_AVAILABLE:

        return 0.0

    try:

        value = get_external_co_occurrence(
            clean_ingredient(ingredient_1),
            clean_ingredient(ingredient_2),
            external_df
        )

        if value is None:

            return 0.0

        return float(value)

    except Exception as e:

        print(
            "External evidence lookup error:",
            str(e)
        )

        return 0.0


# ============================================================
# 15. BUILD FINAL FEATURE VECTOR
# ============================================================

def build_features(
    ingredient_1,
    ingredient_2,
    co_occurrence=0
):

    ingredient_1 = clean_ingredient(ingredient_1)
    ingredient_2 = clean_ingredient(ingredient_2)

    model_text = create_model_text(
        ingredient_1,
        ingredient_2
    )

    # TF-IDF features

    X_text = vectorizer.transform(
        [model_text]
    ).toarray()

    # External evidence

    external_co_occurrence = get_external_value(
        ingredient_1,
        ingredient_2
    )

    external_co_occurrence = max(
        0.0,
        float(external_co_occurrence or 0.0)
    )

    external_co_occurrence_log = np.log1p(
        external_co_occurrence
    )

    external_evidence_indicator = (
        1.0 if external_co_occurrence > 0 else 0.0
    )

    X_external = np.array(
        [[
            external_co_occurrence_log,
            external_evidence_indicator
        ]],
        dtype=float
    )

    X = np.hstack([
        X_text,
        X_external
    ])

    return X, external_co_occurrence


# ============================================================
# 16. VERIFY FEATURE COUNT
# ============================================================

def verify_feature_count(X):

    expected_features = int(
        model.get_booster().num_features()
    )

    actual_features = int(
        X.shape[1]
    )

    if actual_features != expected_features:

        raise ValueError(
            "\nFEATURE SHAPE MISMATCH\n"
            f"Model expects: {expected_features}\n"
            f"Predictor created: {actual_features}\n"
            "The training and prediction feature pipelines do not match."
        )


# ============================================================
# 17. CALCULATE CIRS COMPONENTS
# ============================================================

def calculate_cirs_components(
    dataset_risk,
    co_occurrence,
    external_co_occurrence
):

    severity_map = {
        "Safe": 0,
        "Low": 20,
        "Medium": 60,
        "High": 90
    }

    dataset_risk_clean = str(
        dataset_risk
    ).strip()

    severity_score = severity_map.get(
        dataset_risk_clean,
        0
    )

    co_occurrence_log = np.log1p(
        max(0, float(co_occurrence))
    )

    co_occurrence_score = min(
        100,
        co_occurrence_log * 20
    )

    external_evidence_score = (
        100 if external_co_occurrence > 0 else 0
    )

    if severity_score >= 90:

        interaction_score = 90

    elif severity_score >= 60:

        interaction_score = 60

    elif severity_score >= 20:

        interaction_score = 30

    else:

        interaction_score = 0

    return (
        severity_score,
        co_occurrence_score,
        external_evidence_score,
        interaction_score
    )


# ============================================================
# 18. CALCULATE FINAL CIRS
# ============================================================

def calculate_risk_score(
    dataset_risk,
    co_occurrence,
    external_co_occurrence
):

    (
        severity_score,
        co_occurrence_score,
        external_evidence_score,
        interaction_score
    ) = calculate_cirs_components(
        dataset_risk,
        co_occurrence,
        external_co_occurrence
    )

    cirs = calculate_cirs(
        severity_score,
        co_occurrence_score,
        external_evidence_score,
        interaction_score
    )

    cirs_risk = classify_cirs(cirs)

    return {

        "severity_score": severity_score,

        "co_occurrence_score": co_occurrence_score,

        "external_evidence_score": external_evidence_score,

        "interaction_score": interaction_score,

        "cirs": cirs,

        "cirs_risk": cirs_risk

    }


# ============================================================
# 19. PREDICT RISK
# ============================================================

def predict_risk(
    ingredient_1,
    ingredient_2,
    co_occurrence=0
):

    X, external_co_occurrence = build_features(
        ingredient_1,
        ingredient_2,
        co_occurrence
    )

    verify_feature_count(X)

    probabilities_array = model.predict_proba(X)[0]

    predicted_class = int(
        np.argmax(probabilities_array)
    )

    predicted_class = max(
        0,
        min(
            predicted_class,
            len(RISK_CLASSES) - 1
        )
    )

    predicted_risk = RISK_CLASSES[predicted_class]

    probabilities = {
        RISK_CLASSES[i]: float(probabilities_array[i])
        for i in range(len(RISK_CLASSES))
    }

    print("\nExternal co-occurrence:", external_co_occurrence)
    print("Feature vector shape:", X.shape)
    print("Predicted class:", predicted_class)
    print("Predicted risk:", predicted_risk)

    return (
        predicted_risk,
        probabilities,
        X,
        predicted_class,
        external_co_occurrence
    )


# ============================================================
# 20. SHAP USING XGBOOST BUILT-IN TREESHAP
# ============================================================

def explain_prediction(X):

    try:

        print(
            "\nGenerating SHAP contributions using XGBoost..."
        )

        booster = model.get_booster()

        dmatrix = xgb.DMatrix(X)

        explanation = booster.predict(
            dmatrix,
            pred_contribs=True,
            strict_shape=True
        )

        print("SHAP calculation successful!")

        print(
            "SHAP output shape:",
            explanation.shape
        )

        return explanation

    except Exception as e:

        print("\nSHAP explanation failed:")

        print(type(e).__name__, str(e))

        return None


# ============================================================
# 21. CONVERT SHAP VALUES INTO FRONTEND FORMAT
# ============================================================

def get_shap_explanations(
    explanation,
    predicted_class,
    X=None,
    top_n=5
):

    if explanation is None:

        return []

    try:

        values = np.asarray(explanation)

        print("\nProcessing SHAP contributions...")

        print(
            "SHAP array shape:",
            values.shape
        )

        if values.ndim != 3:

            print("Unexpected SHAP dimensions.")

            return []

        if values.shape[1] != len(RISK_CLASSES):

            print("Unexpected SHAP class dimension.")

            return []

        shap_values = values[
            0,
            predicted_class,
            :-1
        ]

        if (
            feature_names is not None
            and len(feature_names) == len(shap_values)
        ):

            names = [
                str(name)
                for name in feature_names
            ]

        else:

            names = [
                f"Feature_{i}"
                for i in range(len(shap_values))
            ]

        # Only select features that are active in this input.

        if X is not None:

            input_values = np.asarray(X).reshape(-1)

            active_indices = np.flatnonzero(
                np.abs(input_values) > 1e-12
            )

            active_indices = [
                index
                for index in active_indices
                if index < len(shap_values)
            ]

        else:

            active_indices = range(
                len(shap_values)
            )

        results = []

        for index in active_indices:

            value = float(
                shap_values[index]
            )

            if abs(value) < 1e-8:

                continue

            feature = names[index]

            readable_name = (
                feature
                .replace("ING1_", "Ingredient 1: ")
                .replace("ING2_", "Ingredient 2: ")
                .replace("PAIR_", "Ingredient pair: ")
                .replace("_", " ")
            )

            direction = (
                "Supports the predicted class"
                if value > 0
                else "Opposes the predicted class"
            )

            results.append({

                "feature": readable_name,

                "value": round(value, 6),

                "direction": direction

            })

        results.sort(
            key=lambda item: abs(item["value"]),
            reverse=True
        )

        return results[:top_n]

    except Exception as e:

        print("\nSHAP conversion failed:")

        print(type(e).__name__, str(e))

        return []


# ============================================================
# 22. DISPLAY SHAP
# ============================================================

def display_shap(
    shap_results,
    predicted_class
):

    print("\n========================================")
    print("SHAP EXPLANATION")
    print("========================================")

    print(
        "Predicted class:",
        RISK_CLASSES[predicted_class]
    )

    if not shap_results:

        print(
            "No significant SHAP contributions found."
        )

        return

    for item in shap_results:

        print(
            f"{item['feature']}: "
            f"{item['value']:.6f} "
            f"({item['direction']})"
        )


# ============================================================
# 23. DISPLAY CIRS
# ============================================================

def display_cirs(cirs_result):

    print("\n========================================")
    print("COSMETIC INTERACTION RISK SCORE")
    print("========================================")

    print(
        f"Severity Score: "
        f"{cirs_result['severity_score']:.2f}/100"
    )

    print(
        f"Co-occurrence Score: "
        f"{cirs_result['co_occurrence_score']:.2f}/100"
    )

    print(
        f"External Evidence Score: "
        f"{cirs_result['external_evidence_score']:.2f}/100"
    )

    print(
        f"Interaction Score: "
        f"{cirs_result['interaction_score']:.2f}/100"
    )

    print(
        f"\nCIRS Score: "
        f"{cirs_result['cirs']:.2f}/100"
    )

    print(
        "CIRS Risk:",
        cirs_result["cirs_risk"]
    )


# ============================================================
# 24. MAIN
# ============================================================

if __name__ == "__main__":

    print("\n========================================")
    print("COSMETIC CONFLICT RISK PREDICTOR")
    print("========================================")

    ingredient_1 = input(
        "\nEnter first ingredient: "
    )

    ingredient_2 = input(
        "Enter second ingredient: "
    )

    # Dataset lookup

    pair_info = find_pair(
        ingredient_1,
        ingredient_2
    )

    print("\n========================================")
    print("DATASET INFORMATION")
    print("========================================")

    if pair_info["found"]:

        print("Pair found in dataset: YES")

        print(
            "Co-occurrence count:",
            pair_info["co_occurrence"]
        )

        print(
            "Dataset risk:",
            pair_info["dataset_risk"]
        )

        if pair_info["severity_note"]:

            print(
                "Severity explanation:",
                pair_info["severity_note"]
            )

    else:

        print("Pair found in dataset: NO")
        print("This is an unseen ingredient pair.")
        print("Co-occurrence count: 0")

    # External evidence

    external_value = get_external_value(
        ingredient_1,
        ingredient_2
    )

    print(
        "External co-occurrence:",
        external_value
    )

    # XGBoost prediction

    (
        predicted_risk,
        probabilities,
        X,
        predicted_class,
        external_co_occurrence
    ) = predict_risk(
        ingredient_1,
        ingredient_2,
        pair_info["co_occurrence"]
    )

    # CIRS

    cirs_result = calculate_risk_score(
        pair_info["dataset_risk"],
        pair_info["co_occurrence"],
        external_co_occurrence
    )

    # Prediction result

    print("\n========================================")
    print("PREDICTION RESULT")
    print("========================================")

    print("Ingredient 1:", ingredient_1)
    print("Ingredient 2:", ingredient_2)
    print("Predicted Risk:", predicted_risk)

    print("\nRisk Probabilities:")

    for risk, probability in probabilities.items():

        print(
            f"{risk}: {probability * 100:.2f}%"
        )

    # Display CIRS

    display_cirs(cirs_result)

    # SHAP

    print("\nGenerating SHAP explanations...")

    explanation = explain_prediction(X)

    shap_explanation = get_shap_explanations(
        explanation,
        predicted_class,
        X=X,
        top_n=5
    )

    display_shap(
        shap_explanation,
        predicted_class
    )

    print("\n========================================")
    print("SHAP DATA FOR FRONTEND")
    print("========================================")

    print(shap_explanation)

    print("\n========================================")
    print("Prediction completed successfully!")
    print("========================================")
