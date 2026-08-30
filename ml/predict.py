import os
import pickle
import numpy as np
import pandas as pd
import shap

from xgboost import XGBClassifier


# ============================================================
# 1. PATHS
# ============================================================

DATA_PATH = "data/ingredient_pairs_3000_severity.xlsx"
MODEL_DIR = "ml/model"

MODEL_PATH = os.path.join(
    MODEL_DIR,
    "xgboost_risk_model.json"
)

VECTORIZER_PATH = os.path.join(
    MODEL_DIR,
    "tfidf_vectorizer.pkl"
)

CLASSES_PATH = os.path.join(
    MODEL_DIR,
    "risk_classes.npy"
)

FEATURE_NAMES_PATH = os.path.join(
    MODEL_DIR,
    "feature_names.npy"
)


# ============================================================
# 2. LOAD DATASET
# ============================================================

print("\nLoading conflict dataset...")

df = pd.read_excel(
    DATA_PATH
)

df["Ingredient_1"] = (
    df["Ingredient_1"]
    .astype(str)
    .str.lower()
    .str.strip()
)

df["Ingredient_2"] = (
    df["Ingredient_2"]
    .astype(str)
    .str.lower()
    .str.strip()
)

print(
    "Conflict dataset loaded successfully!"
)


# ============================================================
# 3. LOAD MODEL
# ============================================================

print("\nLoading XGBoost model...")

model = XGBClassifier()

model.load_model(
    MODEL_PATH
)

print(
    "XGBoost model loaded successfully!"
)


# ============================================================
# 4. LOAD TF-IDF
# ============================================================

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
# 5. LOAD CLASSES
# ============================================================

risk_classes = np.load(
    CLASSES_PATH,
    allow_pickle=True
)

print(
    "Risk classes loaded successfully!"
)


# ============================================================
# 6. LOAD FEATURE NAMES
# ============================================================

feature_names = np.load(
    FEATURE_NAMES_PATH,
    allow_pickle=True
)


# ============================================================
# 7. FIND DATASET PAIR
# ============================================================

def find_pair(
    ingredient_1,
    ingredient_2
):

    ingredient_1 = (
        ingredient_1
        .lower()
        .strip()
    )

    ingredient_2 = (
        ingredient_2
        .lower()
        .strip()
    )

    # Check both possible orders
    pair = df[
        (
            (df["Ingredient_1"] == ingredient_1)
            &
            (df["Ingredient_2"] == ingredient_2)
        )
        |
        (
            (df["Ingredient_1"] == ingredient_2)
            &
            (df["Ingredient_2"] == ingredient_1)
        )
    ]

    if len(pair) > 0:

        row = pair.iloc[0]

        return {
            "found": True,
            "co_occurrence": float(
                row["Co_Occurrence_Count"]
            ),
            "dataset_risk": str(
                row["Severity"]
            ),
            "severity_note": str(
                row.get(
                    "Severity_Note",
                    ""
                )
            )
        }

    return {
        "found": False,
        "co_occurrence": 0,
        "dataset_risk": None,
        "severity_note": None
    }


# ============================================================
# 8. CREATE FEATURES
# ============================================================

def create_features(
    ingredient_1,
    ingredient_2,
    co_occurrence
):

    ingredient_1 = (
        ingredient_1
        .lower()
        .strip()
    )

    ingredient_2 = (
        ingredient_2
        .lower()
        .strip()
    )

    ingredient_pair = (
        ingredient_1
        + " "
        + ingredient_2
    )

    text_features = vectorizer.transform(
        [ingredient_pair]
    ).toarray()

    count_feature = np.array(
        [[float(co_occurrence)]]
    )

    X = np.hstack([
        text_features,
        count_feature
    ])

    return X


# ============================================================
# 9. PREDICT RISK
# ============================================================

def predict_risk(
    ingredient_1,
    ingredient_2,
    co_occurrence
):

    X = create_features(
        ingredient_1,
        ingredient_2,
        co_occurrence
    )

    prediction = model.predict(
        X
    )

    predicted_class = int(
        prediction[0]
    )

    predicted_risk = str(
        risk_classes[
            predicted_class
        ]
    )

    probabilities = model.predict_proba(
        X
    )[0]

    probability_dict = {}

    for i, risk in enumerate(
        risk_classes
    ):

        probability_dict[
            str(risk)
        ] = float(
            probabilities[i]
        )

    return (
        predicted_risk,
        probability_dict,
        X,
        predicted_class
    )


# ============================================================
# 10. SHAP EXPLANATION
# ============================================================

def explain_prediction(
    X
):

    print(
        "\nGenerating SHAP explanation..."
    )

    # Use generic permutation SHAP because
    # TreeExplainer has compatibility issues
    # with SHAP 0.46.0 and XGBoost 3.4.x.

    background_size = min(
        20,
        X.shape[1]
    )

    # Use zero background for prediction explanation
    background = np.zeros(
        (1, X.shape[1])
    )

    explainer = shap.Explainer(
        model.predict_proba,
        background,
        algorithm="permutation"
    )

    explanation = explainer(
        X
    )

    print(
        "SHAP explanation generated!"
    )

    return explanation


# ============================================================
# 11. DISPLAY SHAP
# ============================================================

def display_shap(
    explanation,
    predicted_class
):

    values = explanation.values

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

        shap_values = values.flatten()


    feature_count = min(
        len(feature_names),
        len(shap_values)
    )

    contributions = []

    for i in range(
        feature_count
    ):

        value = float(
            shap_values[i]
        )

        if abs(value) > 0.000001:

            contributions.append(
                (
                    str(
                        feature_names[i]
                    ),
                    value
                )
            )


    contributions.sort(
        key=lambda x: abs(x[1]),
        reverse=True
    )


    print(
        "\n========================================"
    )

    print(
        "SHAP EXPLANATION"
    )

    print(
        "========================================"
    )


    if not contributions:

        print(
            "No significant feature contribution found."
        )

        return


    print(
        "\nTop contributing features:"
    )


    for feature, value in contributions[:10]:

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


# ============================================================
# 12. MAIN
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
            pair_info["co_occurrence"]
        )

        print(
            "Dataset risk:",
            pair_info["dataset_risk"]
        )

        if pair_info["severity_note"]:

            print(
                "Severity note:",
                pair_info["severity_note"]
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
    # Create prediction
    # --------------------------------------------------------

    (
        predicted_risk,
        probabilities,
        X,
        predicted_class
    ) = predict_risk(
        ingredient_1,
        ingredient_2,
        pair_info["co_occurrence"]
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

    explanation = explain_prediction(
        X
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