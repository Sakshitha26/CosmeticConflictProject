import os
import pickle
import re
import warnings

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

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

OUTPUT_PATH = os.path.join(
    MODEL_DIR,
    "overall_prediction_graph.png"
)


# ============================================================
# 2. CLEAN INGREDIENT
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
# 3. CREATE MODEL TEXT
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

    token_1 = ingredient_1.replace(
        " ",
        "_"
    )

    token_2 = ingredient_2.replace(
        " ",
        "_"
    )

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
# 4. LOAD MODEL
# ============================================================

print("\n========================================")
print("LOADING MODEL")
print("========================================")

model = XGBClassifier()

model.load_model(
    MODEL_PATH
)

print(
    "Model loaded successfully!"
)


# ============================================================
# 5. LOAD TF-IDF
# ============================================================

with open(
    VECTORIZER_PATH,
    "rb"
) as f:

    vectorizer = pickle.load(f)


print(
    "TF-IDF vectorizer loaded successfully!"
)


# ============================================================
# 6. LOAD DATASET
# ============================================================

print("\n========================================")
print("LOADING DATASET")
print("========================================")

df = pd.read_excel(
    DATA_PATH
)

df.columns = (
    df.columns
    .astype(str)
    .str.strip()
)

print(
    "Dataset:",
    DATA_PATH
)

print(
    "Total rows:",
    len(df)
)


# ============================================================
# 7. CLEAN DATA
# ============================================================

df["Ingredient_A"] = (
    df["Ingredient_A"]
    .apply(clean_ingredient)
)

df["Ingredient_B"] = (
    df["Ingredient_B"]
    .apply(clean_ingredient)
)


df = df[
    (df["Ingredient_A"] != "")
    &
    (df["Ingredient_B"] != "")
]


df = df.reset_index(
    drop=True
)


# ============================================================
# 8. CREATE MODEL TEXT
# ============================================================

print("\n========================================")
print("CREATING TF-IDF FEATURES")
print("========================================")

df["Model_Text"] = df.apply(
    lambda row:
        create_model_text(
            row["Ingredient_A"],
            row["Ingredient_B"]
        ),
    axis=1
)


X_text = df["Model_Text"]


X_tfidf = (
    vectorizer
    .transform(X_text)
    .toarray()
)


print(
    "TF-IDF feature shape:",
    X_tfidf.shape
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

    external_available = True

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

    external_available = False


# ============================================================
# 10. EXTERNAL FEATURE FUNCTION
# ============================================================

def get_external_value(
    ingredient_1,
    ingredient_2
):

    if not external_available:

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

        return float(value)

    except Exception:

        return 0.0


# ============================================================
# 11. CREATE EXTERNAL FEATURES
# ============================================================

external_logs = []
external_indicators = []


print(
    "\nCreating external evidence features..."
)


for _, row in df.iterrows():

    value = get_external_value(
        row["Ingredient_A"],
        row["Ingredient_B"]
    )

    external_logs.append(
        np.log1p(value)
    )

    external_indicators.append(
        1.0 if value > 0 else 0.0
    )


X_external_log = np.array(
    external_logs
).reshape(-1, 1)


X_external_indicator = np.array(
    external_indicators
).reshape(-1, 1)


# ============================================================
# 12. FINAL FEATURE MATRIX
# ============================================================

X = np.hstack([

    X_tfidf,

    X_external_log,

    X_external_indicator

])


print(
    "\nFinal feature shape:",
    X.shape
)


# ============================================================
# 13. CHECK FEATURE COUNT
# ============================================================

expected_features = (
    model.get_booster()
    .num_features()
)

actual_features = X.shape[1]


print(
    "\nExpected model features:",
    expected_features
)

print(
    "Actual features:",
    actual_features
)


if expected_features != actual_features:

    raise ValueError(
        "\nFEATURE MISMATCH!\n"
        f"Model expects {expected_features} features "
        f"but generated {actual_features}."
    )


print(
    "\nFeature count matches the trained model!"
)


# ============================================================
# 14. PREDICTIONS
# ============================================================

print("\n========================================")
print("GENERATING PREDICTIONS")
print("========================================")


predictions = model.predict(
    X
)


predictions = predictions.astype(
    int
)


# ============================================================
# 15. RISK CLASS NAMES
# ============================================================

risk_classes = {
    0: "Safe",
    1: "Medium Risk",
    2: "High Risk"
}


prediction_names = [

    risk_classes[int(prediction)]

    for prediction in predictions

]


# ============================================================
# 16. COUNT PREDICTIONS
# ============================================================

prediction_counts = {

    "Safe":
        prediction_names.count(
            "Safe"
        ),

    "Medium Risk":
        prediction_names.count(
            "Medium Risk"
        ),

    "High Risk":
        prediction_names.count(
            "High Risk"
        )

}


# ============================================================
# 17. PRINT RESULTS
# ============================================================

print("\n========================================")
print("OVERALL PREDICTION RESULTS")
print("========================================")


total_predictions = len(
    prediction_names
)


for category, count in prediction_counts.items():

    percentage = (
        count /
        total_predictions
        * 100
    )

    print(
        f"{category}: "
        f"{count} "
        f"({percentage:.2f}%)"
    )


print(
    "\nTotal predictions:",
    total_predictions
)


# ============================================================
# 18. CREATE GRAPH
# ============================================================

categories = [
    "Safe",
    "Medium Risk",
    "High Risk"
]


values = [

    prediction_counts[
        "Safe"
    ],

    prediction_counts[
        "Medium Risk"
    ],

    prediction_counts[
        "High Risk"
    ]

]


plt.figure(
    figsize=(9, 6)
)


bars = plt.bar(
    categories,
    values
)


plt.title(
    "Overall XGBoost Risk Predictions",
    fontsize=16
)


plt.xlabel(
    "Risk Category"
)


plt.ylabel(
    "Number of Predictions"
)


plt.grid(
    axis="y",
    linestyle="--",
    alpha=0.3
)


# ============================================================
# 19. ADD VALUES + PERCENTAGES
# ============================================================

for bar, value in zip(
    bars,
    values
):

    percentage = (
        value /
        total_predictions
        * 100
    )

    plt.text(

        bar.get_x()
        + bar.get_width() / 2,

        value,

        f"{value}\n"
        f"({percentage:.2f}%)",

        ha="center",

        va="bottom",

        fontsize=11

    )


plt.tight_layout()


# ============================================================
# 20. SAVE GRAPH
# ============================================================

plt.savefig(
    OUTPUT_PATH,
    dpi=300,
    bbox_inches="tight"
)


plt.show()


print(
    "\n========================================"
)

print(
    "GRAPH CREATED SUCCESSFULLY"
)

print(
    "========================================"
)

print(
    "\nSaved at:"
)

print(
    OUTPUT_PATH
)