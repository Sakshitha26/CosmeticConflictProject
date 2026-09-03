
import os
import pickle
import re
import warnings

import numpy as np
import pandas as pd
import shap

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
    "ingredient_pairs_augmented.xlsx"
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
# 3. CLEAN INGREDIENT
# ============================================================

def clean_ingredient(value):

    value = str(value).lower().strip()

    value = value.replace(
        "-",
        " "
    )

    value = value.replace(
        "_",
        " "
    )

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
# 4. LOAD DATASET
# ============================================================

print("\n========================================")
print("LOADING PREDICTION DATA")
print("========================================")


if not os.path.exists(DATA_PATH):

    raise FileNotFoundError(
        f"Dataset not found:\n{DATA_PATH}"
    )


df = pd.read_excel(
    DATA_PATH
)


df["Ingredient_1"] = (
    df["Ingredient_1"]
    .apply(clean_ingredient)
)


df["Ingredient_2"] = (
    df["Ingredient_2"]
    .apply(clean_ingredient)
)


# ------------------------------------------------------------
# IMPORTANT:
# ingredient_pairs_augmented.xlsx does not contain
# Co_Occurrence_Count.
#
# The trained model expects this feature, so when the
# prediction dataset does not contain it, use 0.
# ------------------------------------------------------------

if "Co_Occurrence_Count" not in df.columns:

    df["Co_Occurrence_Count"] = 0


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


print(
    "Prediction dataset loaded successfully!"
)

print(
    "Rows:",
    len(df)
)


# ============================================================
# 5. LOAD MODEL
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


model.load_model(
    MODEL_PATH
)


print(
    "XGBoost model loaded successfully!"
)


# ============================================================
# 6. LOAD TF-IDF
# ============================================================

print("\n========================================")
print("LOADING TF-IDF VECTORIZER")
print("========================================")


if not os.path.exists(
    VECTORIZER_PATH
):

    raise FileNotFoundError(
        f"TF-IDF vectorizer not found:\n"
        f"{VECTORIZER_PATH}"
    )


with open(
    VECTORIZER_PATH,
    "rb"
) as f:

    vectorizer = pickle.load(
        f
    )


print(
    "TF-IDF vectorizer loaded successfully!"
)


# ============================================================
# 7. LOAD RISK CLASSES
# ============================================================

if os.path.exists(
    RISK_CLASSES_PATH
):

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
# 8. LOAD FEATURE NAMES
# ============================================================

feature_names = None


if os.path.exists(
    FEATURE_NAMES_PATH
):

    feature_names = np.load(
        FEATURE_NAMES_PATH,
        allow_pickle=True
    )


# ============================================================
# 9. LOAD EXTERNAL EVIDENCE
# ============================================================

print("\n========================================")
print("LOADING EXTERNAL EVIDENCE")
print("========================================")


try:

    from external_evidence import (
        load_external_evidence,
        get_external_co_occurrence
    )

    external_df = (
        load_external_evidence()
    )

    EXTERNAL_EVIDENCE_AVAILABLE = True

    print(
        "External evidence loaded successfully!"
    )

except Exception as e:

    print(
        "External evidence could not be loaded."
    )

    print(
        "Error:",
        str(e)
    )

    external_df = None

    EXTERNAL_EVIDENCE_AVAILABLE = False


# ============================================================
# 10. CREATE MODEL TEXT
# ============================================================

def create_model_text(
    ingredient_1,
    ingredient_2
):

    ingredient_1 = clean_ingredient(
        ingredient_1
    )

    ingredient_2 = clean_ingredient(
        ingredient_2
    )

    token_1 = (
        ingredient_1
        .replace(
            " ",
            "_"
        )
    )

    token_2 = (
        ingredient_2
        .replace(
            " ",
            "_"
        )
    )

    canonical_pair = "||".join(

        sorted([
            ingredient_1,
            ingredient_2
        ])

    )

    pair_token = (
        canonical_pair
        .replace(
            "||",
            "__"
        )
        .replace(
            " ",
            "_"
        )
    )

    ingredient_text = (

        "ING1_"
        + token_1

        + " "

        + "ING2_"
        + token_2

    )

    pair_text = (

        "PAIR_"
        + pair_token

    )

    return (

        ingredient_text
        + " "
        + pair_text

    )


# ============================================================
# 11. CREATE CANONICAL PAIR
# ============================================================

def create_canonical_pair(
    ingredient_1,
    ingredient_2
):

    ingredient_1 = clean_ingredient(
        ingredient_1
    )

    ingredient_2 = clean_ingredient(
        ingredient_2
    )

    return "||".join(

        sorted([
            ingredient_1,
            ingredient_2
        ])

    )


# ============================================================
# 12. FIND PAIR IN AUGMENTED DATASET
# ============================================================

def find_pair(
    ingredient_1,
    ingredient_2
):

    ingredient_1 = clean_ingredient(
        ingredient_1
    )

    ingredient_2 = clean_ingredient(
        ingredient_2
    )

    # --------------------------------------------------------
    # Direct orientation
    # --------------------------------------------------------

    direct = df[
        (
            df["Ingredient_1"]
            == ingredient_1
        )
        &
        (
            df["Ingredient_2"]
            == ingredient_2
        )
    ]


    # --------------------------------------------------------
    # Reverse orientation
    # --------------------------------------------------------

    reverse = df[
        (
            df["Ingredient_1"]
            == ingredient_2
        )
        &
        (
            df["Ingredient_2"]
            == ingredient_1
        )
    ]


    if len(direct) > 0:

        row = direct.iloc[0]

        return {

            "found": True,

            "co_occurrence": float(
                row[
                    "Co_Occurrence_Count"
                ]
            ),

            "dataset_risk":
                str(
                    row["Severity"]
                ).title(),

            "severity_note":
                (
                    str(
                        row["Severity_Note"]
                    )
                    if "Severity_Note" in row
                    and not pd.isna(
                        row["Severity_Note"]
                    )
                    else ""
                )

        }


    if len(reverse) > 0:

        row = reverse.iloc[0]

        return {

            "found": True,

            "co_occurrence": float(
                row[
                    "Co_Occurrence_Count"
                ]
            ),

            "dataset_risk":
                str(
                    row["Severity"]
                ).title(),

            "severity_note":
                (
                    str(
                        row["Severity_Note"]
                    )
                    if "Severity_Note" in row
                    and not pd.isna(
                        row["Severity_Note"]
                    )
                    else ""
                )

        }


    return {

        "found": False,

        "co_occurrence": 0.0,

        "dataset_risk":
            None,

        "severity_note":
            ""

    }


# ============================================================
# 13. GET EXTERNAL CO-OCCURRENCE
# ============================================================

def get_external_value(
    ingredient_1,
    ingredient_2
):

    if not EXTERNAL_EVIDENCE_AVAILABLE:

        return 0.0


    try:

        value = (
            get_external_co_occurrence(

                clean_ingredient(
                    ingredient_1
                ),

                clean_ingredient(
                    ingredient_2
                ),

                external_df

            )
        )

        if value is None:

            return 0.0

        return float(
            value
        )

    except Exception as e:

        print(
            "External evidence lookup error:",
            str(e)
        )

        return 0.0


# ============================================================
# 14. BUILD FINAL FEATURE VECTOR
# ============================================================

def build_features(
    ingredient_1,
    ingredient_2,
    co_occurrence
):

    # --------------------------------------------------------
    # Clean input
    # --------------------------------------------------------

    ingredient_1 = clean_ingredient(
        ingredient_1
    )

    ingredient_2 = clean_ingredient(
        ingredient_2
    )


    # --------------------------------------------------------
    # Model text
    # --------------------------------------------------------

    model_text = create_model_text(

        ingredient_1,

        ingredient_2

    )


    # --------------------------------------------------------
    # TF-IDF
    # --------------------------------------------------------

    X_text = (

        vectorizer
        .transform(
            [model_text]
        )
        .toarray()

    )


    # --------------------------------------------------------
    # Internal co-occurrence
    #
    # IMPORTANT:
    # Training uses log1p(Co_Occurrence_Count)
    # --------------------------------------------------------

    co_occurrence = float(
        co_occurrence
    )


    co_occurrence_log = np.log1p(
        co_occurrence
    )


    # --------------------------------------------------------
    # External evidence
    # --------------------------------------------------------

    external_co_occurrence = (
        get_external_value(

            ingredient_1,

            ingredient_2

        )
    )


    external_co_occurrence_log = (
        np.log1p(
            external_co_occurrence
        )
    )


    # --------------------------------------------------------
    # External evidence indicator
    # --------------------------------------------------------

    external_evidence_indicator = (

        1.0

        if external_co_occurrence > 0

        else 0.0

    )


    # --------------------------------------------------------
    # Final feature vector
    # --------------------------------------------------------

    X = np.hstack([

        X_text,

        np.array([
            [co_occurrence_log]
        ]),

        np.array([
            [external_co_occurrence_log]
        ]),

        np.array([
            [external_evidence_indicator]
        ])

    ])


    return (

        X,

        external_co_occurrence

    )


# ============================================================
# 15. VERIFY FEATURE COUNT
# ============================================================

def verify_feature_count(X):

    expected_features = int(
        model.get_booster()
        .num_features()
    )

    actual_features = int(
        X.shape[1]
    )


    if actual_features != expected_features:

        raise ValueError(

            "\nFEATURE SHAPE MISMATCH\n"

            f"Model expects: "
            f"{expected_features}\n"

            f"Predictor created: "
            f"{actual_features}\n\n"

            "The training and prediction "
            "feature pipelines do not match."

        )


# ============================================================
# 16. PREDICT RISK
# ============================================================

def predict_risk(
    ingredient_1,
    ingredient_2,
    co_occurrence=0
):

    # --------------------------------------------------------
    # Build features
    # --------------------------------------------------------

    X, external_co_occurrence = (
        build_features(

            ingredient_1,

            ingredient_2,

            co_occurrence

        )
    )


    # --------------------------------------------------------
    # Verify exact model dimensions
    # --------------------------------------------------------

    verify_feature_count(
        X
    )


    # --------------------------------------------------------
    # Prediction probabilities
    # --------------------------------------------------------

    probabilities_array = (

        model
        .predict_proba(
            X
        )[0]

    )


    # --------------------------------------------------------
    # Predicted class
    # --------------------------------------------------------

    predicted_class = int(

        np.argmax(
            probabilities_array
        )

    )


    # --------------------------------------------------------
    # Safety check
    # --------------------------------------------------------

    if predicted_class < 0:

        predicted_class = 0


    if predicted_class >= len(
        RISK_CLASSES
    ):

        predicted_class = (
            len(RISK_CLASSES) - 1
        )


    predicted_risk = (
        RISK_CLASSES[
            predicted_class
        ]
    )


    # --------------------------------------------------------
    # Probability dictionary
    # --------------------------------------------------------

    probabilities = {

        "Safe":
            float(
                probabilities_array[0]
            ),

        "Medium Risk":
            float(
                probabilities_array[1]
            ),

        "High Risk":
            float(
                probabilities_array[2]
            )

    }


    print(
        "\nExternal co-occurrence:",
        external_co_occurrence
    )


    print(
        "Feature vector shape:",
        X.shape
    )


    print(
        "Predicted class:",
        predicted_class
    )


    print(
        "Predicted risk:",
        predicted_risk
    )


    return (

        predicted_risk,

        probabilities,

        X,

        predicted_class

    )


# ============================================================
# 17. SHAP EXPLANATION
# ============================================================

def explain_prediction(
    X
):

    try:

        # ----------------------------------------------------
        # Small background for faster permutation SHAP
        # ----------------------------------------------------

        background = np.zeros(
            (
                1,
                X.shape[1]
            ),
            dtype=float
        )


        # ----------------------------------------------------
        # SHAP permutation explainer
        # ----------------------------------------------------

        explainer = shap.Explainer(

            model.predict_proba,

            background,

            algorithm="permutation"

        )


        explanation = explainer(
            X
        )


        return explanation


    except Exception as e:

        print(
            "\nSHAP explanation failed:"
        )

        print(
            type(e).__name__
        )

        print(
            str(e)
        )

        return None


# ============================================================
# 18. DISPLAY SHAP
# ============================================================

def display_shap(
    explanation,
    predicted_class
):

    if explanation is None:

        print(
            "\nSHAP explanation unavailable."
        )

        return


    try:

        values = (
            explanation.values
        )


        if values.ndim == 3:

            shap_values = values[
                0,
                :,
                predicted_class
            ]

        elif values.ndim == 2:

            shap_values = values[
                0
            ]

        else:

            print(
                "Unexpected SHAP shape:",
                values.shape
            )

            return


        # ----------------------------------------------------
        # Feature names
        # ----------------------------------------------------

        if (
            feature_names is not None
            and len(feature_names)
            == len(shap_values)
        ):

            names = [
                str(x)
                for x in feature_names
            ]

        else:

            names = [

                f"Feature_{i}"

                for i in range(
                    len(shap_values)
                )

            ]


        # ----------------------------------------------------
        # Get strongest SHAP features
        # ----------------------------------------------------

        top_indices = np.argsort(

            np.abs(
                shap_values
            )

        )[::-1][:10]


        print(
            "\n========================================"
        )

        print(
            "SHAP EXPLANATION"
        )

        print(
            "========================================"
        )


        print(
            "Predicted class:",
            RISK_CLASSES[
                predicted_class
            ]
        )


        print(
            "\nTop contributing features:"
        )


        shown = 0


        for index in top_indices:

            value = float(
                shap_values[index]
            )


            # Skip negligible values
            if abs(value) < 1e-8:

                continue


            feature = names[
                index
            ]


            if value > 0:

                direction = (
                    "increases predicted risk"
                )

            else:

                direction = (
                    "decreases predicted risk"
                )


            print(

                f"{feature}: "
                f"{value:.6f} "
                f"({direction})"

            )


            shown += 1


            if shown >= 10:

                break


        if shown == 0:

            print(
                "No significant SHAP contributions found."
            )


    except Exception as e:

        print(
            "\nUnable to display SHAP:"
        )

        print(
            type(e).__name__
        )

        print(
            str(e)
        )


# ============================================================
# 19. MAIN
# ============================================================

if __name__ == "__main__":

    print(
        "\n========================================"
    )

    print(
        "COSMETIC CONFLICT RISK PREDICTOR"
    )

    print(
        "========================================"
    )


    # --------------------------------------------------------
    # Input
    # --------------------------------------------------------

    ingredient_1 = input(
        "\nEnter first ingredient: "
    )


    ingredient_2 = input(
        "Enter second ingredient: "
    )


    # --------------------------------------------------------
    # Search dataset
    # --------------------------------------------------------

    pair_info = find_pair(

        ingredient_1,

        ingredient_2

    )


    # --------------------------------------------------------
    # Dataset information
    # --------------------------------------------------------

    print(
        "\n========================================"
    )

    print(
        "DATASET INFORMATION"
    )

    print(
        "========================================"
    )


    if pair_info["found"]:

        print(
            "Pair found in dataset: YES"
        )


        print(
            "Co-occurrence count:",
            pair_info[
                "co_occurrence"
            ]
        )


        print(
            "Dataset risk:",
            pair_info[
                "dataset_risk"
            ]
        )


        if pair_info[
            "severity_note"
        ]:

            print(
                "Severity note:",
                pair_info[
                    "severity_note"
                ]
            )


    else:

        print(
            "Pair found in dataset: NO"
        )


        print(
            "This is an unseen ingredient pair."
        )


        print(
            "Co-occurrence count: 0"
        )


    # --------------------------------------------------------
    # External evidence preview
    # --------------------------------------------------------

    external_value = (
        get_external_value(

            ingredient_1,

            ingredient_2

        )
    )


    print(
        "External co-occurrence:",
        external_value
    )


    # --------------------------------------------------------
    # Prediction
    # --------------------------------------------------------

    (
        predicted_risk,

        probabilities,

        X,

        predicted_class

    ) = predict_risk(

        ingredient_1,

        ingredient_2,

        pair_info[
            "co_occurrence"
        ]

    )


    # --------------------------------------------------------
    # Prediction result
    # --------------------------------------------------------

    print(
        "\n========================================"
    )

    print(
        "PREDICTION RESULT"
    )

    print(
        "========================================"
    )


    print(
        "Ingredient 1:",
        ingredient_1
    )


    print(
        "Ingredient 2:",
        ingredient_2
    )


    print(
        "\nPredicted Risk:",
        predicted_risk
    )


    # --------------------------------------------------------
    # Probabilities
    # --------------------------------------------------------

    print(
        "\nRisk Probabilities:"
    )


    for risk, probability in (
        probabilities.items()
    ):

        print(

            f"{risk}: "
            f"{probability * 100:.2f}%"

        )


    # --------------------------------------------------------
    # SHAP
    # --------------------------------------------------------

    explanation = (
        explain_prediction(
            X
        )
    )


    display_shap(

        explanation,

        predicted_class

    )


    # --------------------------------------------------------
    # Final
    # --------------------------------------------------------

    print(
        "\n========================================"
    )

    print(
        "Prediction completed successfully!"
    )

    print(
        "========================================"
    )

