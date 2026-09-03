import os
import pickle
import re
import warnings

import numpy as np
import pandas as pd
import shap

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    balanced_accuracy_score,
    f1_score,
    precision_score,
    recall_score
)
from sklearn.utils.class_weight import compute_sample_weight

from xgboost import XGBClassifier

from external_evidence import (
    load_external_evidence,
    get_external_co_occurrence
)


warnings.filterwarnings("ignore")


# ============================================================
# 1. PATHS
# ============================================================

DATA_PATH = "data/ingredient_pairs_augmented.xlsx"

MODEL_DIR = "ml/model"

os.makedirs(
    MODEL_DIR,
    exist_ok=True
)


# ============================================================
# 2. LOAD DATASET
# ============================================================

print("\n========================================")
print("LOADING COSMETIC CONFLICT DATASET")
print("========================================")

if not os.path.exists(DATA_PATH):

    raise FileNotFoundError(
        f"\nDataset not found:\n{DATA_PATH}\n"
        "Run this script from the project root."
    )


df = pd.read_excel(DATA_PATH)

print("Dataset loaded successfully!")
print("Rows:", len(df))
print("Columns:", df.columns.tolist())


# ============================================================
# 3. REQUIRED COLUMNS
# ============================================================

required_columns = [
    "Ingredient_1",
    "Ingredient_2",
    "Severity"
]

missing = [c for c in required_columns if c not in df.columns]

if missing:
    raise ValueError(
        f"Missing required columns: {missing}"
    )

# Co_Occurrence_Count is optional in the augmented dataset.
# If it is missing, use 0 as the internal co-occurrence value.
if "Co_Occurrence_Count" not in df.columns:
    print("Co_Occurrence_Count not found.")
    print("Creating Co_Occurrence_Count = 0 for all rows.")
    df["Co_Occurrence_Count"] = 0


# ============================================================
# 4. CLEAN DATA
# ============================================================

print("\n========================================")
print("CLEANING DATASET")
print("========================================")


df = df.dropna(
    subset=required_columns
).copy()


def clean_ingredient(value):

    value = str(value).lower().strip()

    # Replace separators
    value = value.replace("-", " ")
    value = value.replace("_", " ")

    # Remove special characters
    value = re.sub(
        r"[^a-z0-9\s]",
        " ",
        value
    )

    # Remove repeated spaces
    value = re.sub(
        r"\s+",
        " ",
        value
    ).strip()

    return value


df["Ingredient_1"] = (
    df["Ingredient_1"]
    .apply(clean_ingredient)
)


df["Ingredient_2"] = (
    df["Ingredient_2"]
    .apply(clean_ingredient)
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


# ============================================================
# 5. RISK MAPPING
# ============================================================

risk_mapping = {

    "safe": 0,

    "medium": 1,

    "medium risk": 1,

    "high": 2,

    "high risk": 2

}


df = df[
    df["Severity"].isin(
        risk_mapping.keys()
    )
].copy()


df["Risk_Label"] = (
    df["Severity"]
    .map(risk_mapping)
)


# ============================================================
# 6. REMOVE ONLY EXACT DUPLICATES
# ============================================================

print("\nRemoving exact duplicate rows...")


before_duplicates = len(df)


df = df.drop_duplicates(
    subset=[
        "Ingredient_1",
        "Ingredient_2",
        "Co_Occurrence_Count",
        "Severity"
    ]
).reset_index(drop=True)


after_duplicates = len(df)


print(
    "Exact duplicates removed:",
    before_duplicates - after_duplicates
)


print(
    "Rows after cleaning:",
    len(df)
)


# ============================================================
# 7. CREATE CANONICAL PAIR
# ============================================================

"""
Canonical pair is used as an additional feature.

Example:

retinol + salicylic acid

and

salicylic acid + retinol

produce the same canonical pair.

We DO NOT remove rows using this field because the
augmented dataset may contain useful repeated evidence.
"""


df["Canonical_Pair"] = df.apply(

    lambda row:
    "||".join(
        sorted([
            row["Ingredient_1"],
            row["Ingredient_2"]
        ])
    ),

    axis=1

)


# ============================================================
# 8. LOAD EXTERNAL EVIDENCE
# ============================================================

print("\n========================================")
print("LOADING EXTERNAL EVIDENCE")
print("========================================")


external_df = load_external_evidence()


# ============================================================
# 9. EXTERNAL CO-OCCURRENCE
# ============================================================

print("\n========================================")
print("ADDING EXTERNAL EVIDENCE")
print("========================================")


df["External_Co_Occurrence"] = df.apply(

    lambda row:

    get_external_co_occurrence(

        row["Ingredient_1"],

        row["Ingredient_2"],

        external_df

    ),

    axis=1

)


# Log transformation prevents very large
# external counts from dominating the model.

df["External_Co_Occurrence_Log"] = np.log1p(
    df["External_Co_Occurrence"]
)


print(
    "External evidence feature added!"
)


print(
    "Pairs with external evidence:",
    int(
        (
            df["External_Co_Occurrence"] > 0
        ).sum()
    )
)


print(
    "Maximum external co-occurrence:",
    float(
        df["External_Co_Occurrence"].max()
    )
)


# ============================================================
# 10. INTERNAL CO-OCCURRENCE
# ============================================================

df["Co_Occurrence_Log"] = np.log1p(
    df["Co_Occurrence_Count"]
)


# ============================================================
# 11. RISK DISTRIBUTION
# ============================================================

print("\n========================================")
print("RISK DISTRIBUTION")
print("========================================")


distribution = (
    df["Severity"]
    .value_counts()
)


print(distribution)


print("\nClass counts:")


print(
    "Safe:",
    distribution.get(
        "safe",
        0
    )
)


print(
    "Medium Risk:",
    distribution.get(
        "medium risk",
        0
    ) +
    distribution.get(
        "medium",
        0
    )
)


print(
    "High Risk:",
    distribution.get(
        "high risk",
        0
    ) +
    distribution.get(
        "high",
        0
    )
)


# ============================================================
# 12. CREATE TARGET
# ============================================================

y = df[
    "Risk_Label"
].astype(int).values


print("\nRisk mapping:")
print("0 = Safe")
print("1 = Medium Risk")
print("2 = High Risk")


# ============================================================
# 13. CREATE INGREDIENT FEATURES
# ============================================================

print("\n========================================")
print("CREATING INGREDIENT FEATURES")
print("========================================")


def ingredient_token(value):

    return (
        str(value)
        .replace(" ", "_")
        .strip()
    )


df["Ingredient_1_Token"] = (
    df["Ingredient_1"]
    .apply(ingredient_token)
)


df["Ingredient_2_Token"] = (
    df["Ingredient_2"]
    .apply(ingredient_token)
)


df["Pair_Token"] = (
    df["Canonical_Pair"]
    .str.replace(
        "||",
        "__",
        regex=False
    )
    .str.replace(
        " ",
        "_",
        regex=False
    )
)


# ------------------------------------------------------------
# Ingredient identity
# ------------------------------------------------------------

df["Ingredient_Text"] = (

    "ING1_"
    + df["Ingredient_1_Token"]

    + " "

    + "ING2_"
    + df["Ingredient_2_Token"]

)


# ------------------------------------------------------------
# Explicit pair identity
# ------------------------------------------------------------

df["Pair_Text"] = (

    "PAIR_"
    + df["Pair_Token"]

)


# ------------------------------------------------------------
# Combined model text
# ------------------------------------------------------------

df["Model_Text"] = (

    df["Ingredient_Text"]

    + " "

    + df["Pair_Text"]

)


# ============================================================
# 14. TRAIN / TEST SPLIT
# ============================================================

print("\n========================================")
print("TRAIN / TEST SPLIT")
print("========================================")


(
    text_train,
    text_test,

    y_train,
    y_test,

    count_train,
    count_test,

    ext_train,
    ext_test

) = train_test_split(

    df["Model_Text"],

    y,

    df["Co_Occurrence_Log"].values,

    df["External_Co_Occurrence_Log"].values,

    test_size=0.20,

    random_state=42,

    stratify=y

)


print(
    "Training samples:",
    len(y_train)
)


print(
    "Testing samples:",
    len(y_test)
)


# ============================================================
# 15. CHECK TRAINING CLASS DISTRIBUTION
# ============================================================

print("\nTraining class distribution:")


unique_train, counts_train = np.unique(
    y_train,
    return_counts=True
)


for class_id, count in zip(
    unique_train,
    counts_train
):

    if class_id == 0:
        name = "Safe"

    elif class_id == 1:
        name = "Medium Risk"

    else:
        name = "High Risk"

    print(
        f"{name}: {count}"
    )


# ============================================================
# 16. TF-IDF
# ============================================================

print("\n========================================")
print("CREATING TF-IDF FEATURES")
print("========================================")


vectorizer = TfidfVectorizer(

    token_pattern=r"(?u)\b[A-Za-z0-9_]+\b",

    ngram_range=(1, 2),

    min_df=1,

    sublinear_tf=True,

    max_features=10000

)


X_train_text = (

    vectorizer
    .fit_transform(
        text_train
    )
    .toarray()

)


X_test_text = (

    vectorizer
    .transform(
        text_test
    )
    .toarray()

)


print(
    "TF-IDF training shape:",
    X_train_text.shape
)


print(
    "TF-IDF testing shape:",
    X_test_text.shape
)


# ============================================================
# 17. NUMERICAL PAIR FEATURES
# ============================================================

print("\n========================================")
print("CREATING NUMERICAL FEATURES")
print("========================================")


# ------------------------------------------------------------
# Feature 1:
# Internal co-occurrence
# ------------------------------------------------------------

train_internal = (
    count_train
    .reshape(-1, 1)
)


test_internal = (
    count_test
    .reshape(-1, 1)
)


# ------------------------------------------------------------
# Feature 2:
# External co-occurrence
# ------------------------------------------------------------

train_external = (
    ext_train
    .reshape(-1, 1)
)


test_external = (
    ext_test
    .reshape(-1, 1)
)


# ------------------------------------------------------------
# Feature 3:
# External evidence indicator
#
# 1 = external evidence exists
# 0 = no external evidence
# ------------------------------------------------------------

train_external_indicator = (
    (ext_train > 0)
    .astype(float)
    .reshape(-1, 1)
)


test_external_indicator = (
    (ext_test > 0)
    .astype(float)
    .reshape(-1, 1)
)


# ============================================================
# 18. FINAL ML FEATURES
# ============================================================

X_train = np.hstack([

    X_train_text,

    train_internal,

    train_external,

    train_external_indicator

])


X_test = np.hstack([

    X_test_text,

    test_internal,

    test_external,

    test_external_indicator

])


print(
    "\nFinal training feature shape:",
    X_train.shape
)


print(
    "Final testing feature shape:",
    X_test.shape
)


print(
    "Total features:",
    X_train.shape[1]
)


# ============================================================
# 19. CLASS IMBALANCE
# ============================================================

print("\n========================================")
print("HANDLING CLASS IMBALANCE")
print("========================================")


sample_weights = compute_sample_weight(

    class_weight="balanced",

    y=y_train

)


print(
    "Sample weights generated successfully!"
)


print(
    "Minimum weight:",
    round(
        float(
            sample_weights.min()
        ),
        4
    )
)


print(
    "Maximum weight:",
    round(
        float(
            sample_weights.max()
        ),
        4
    )
)


# ============================================================
# 20. TRAIN XGBOOST
# ============================================================

print("\n========================================")
print("TRAINING XGBOOST")
print("========================================")


model = XGBClassifier(

    n_estimators=400,

    max_depth=4,

    learning_rate=0.035,

    subsample=0.90,

    colsample_bytree=0.85,

    min_child_weight=1,

    gamma=0.0,

    reg_alpha=0.1,

    reg_lambda=1.5,

    objective="multi:softprob",

    num_class=3,

    eval_metric="mlogloss",

    random_state=42,

    n_jobs=-1

)


model.fit(

    X_train,

    y_train,

    sample_weight=sample_weights

)


print(
    "XGBoost training completed!"
)


# ============================================================
# 21. PREDICTION
# ============================================================

print("\nMaking predictions...")


y_pred = model.predict(
    X_test
)


y_probability = model.predict_proba(
    X_test
)


# ============================================================
# 22. METRICS
# ============================================================

accuracy = accuracy_score(
    y_test,
    y_pred
)


balanced_accuracy = (
    balanced_accuracy_score(
        y_test,
        y_pred
    )
)


macro_f1 = f1_score(

    y_test,

    y_pred,

    average="macro",

    zero_division=0

)


macro_precision = precision_score(

    y_test,

    y_pred,

    average="macro",

    zero_division=0

)


macro_recall = recall_score(

    y_test,

    y_pred,

    average="macro",

    zero_division=0

)


# ============================================================
# 23. RESULTS
# ============================================================

print("\n========================================")
print("XGBOOST MODEL RESULTS")
print("========================================")


print(
    "Accuracy:",
    round(
        accuracy * 100,
        2
    ),
    "%"
)


print(
    "Balanced Accuracy:",
    round(
        balanced_accuracy * 100,
        2
    ),
    "%"
)


print(
    "Macro Precision:",
    round(
        macro_precision,
        4
    )
)


print(
    "Macro Recall:",
    round(
        macro_recall,
        4
    )
)


print(
    "Macro F1:",
    round(
        macro_f1,
        4
    )
)


# ============================================================
# 24. CLASSIFICATION REPORT
# ============================================================

print("\n========================================")
print("CLASSIFICATION REPORT")
print("========================================")


print(

    classification_report(

        y_test,

        y_pred,

        labels=[
            0,
            1,
            2
        ],

        target_names=[
            "Safe",
            "Medium Risk",
            "High Risk"
        ],

        zero_division=0

    )

)


# ============================================================
# 25. CONFUSION MATRIX
# ============================================================

print("\n========================================")
print("CONFUSION MATRIX")
print("========================================")


cm = confusion_matrix(

    y_test,

    y_pred,

    labels=[
        0,
        1,
        2
    ]

)


cm_df = pd.DataFrame(

    cm,

    index=[
        "Actual Safe",
        "Actual Medium Risk",
        "Actual High Risk"
    ],

    columns=[
        "Predicted Safe",
        "Predicted Medium Risk",
        "Predicted High Risk"
    ]

)


print(
    cm_df
)


# ============================================================
# 26. SAVE XGBOOST MODEL
# ============================================================

model_path = os.path.join(

    MODEL_DIR,

    "xgboost_risk_model.json"

)


model.save_model(
    model_path
)


print(
    "\nXGBoost model saved:"
)


print(
    model_path
)


# ============================================================
# 27. SAVE TF-IDF VECTORIZER
# ============================================================

vectorizer_path = os.path.join(

    MODEL_DIR,

    "tfidf_vectorizer.pkl"

)


with open(

    vectorizer_path,

    "wb"

) as f:

    pickle.dump(

        vectorizer,

        f

    )


print(
    "TF-IDF vectorizer saved:"
)


print(
    vectorizer_path
)


# ============================================================
# 28. SAVE RISK CLASSES
# ============================================================

risk_classes = np.array([

    "Safe",

    "Medium Risk",

    "High Risk"

])


np.save(

    os.path.join(

        MODEL_DIR,

        "risk_classes.npy"

    ),

    risk_classes

)


# ============================================================
# 29. SAVE FEATURE NAMES
# ============================================================

feature_names = list(

    vectorizer
    .get_feature_names_out()

)


feature_names.append(
    "Co_Occurrence_Log"
)


feature_names.append(
    "External_Co_Occurrence_Log"
)


feature_names.append(
    "External_Evidence_Indicator"
)


np.save(

    os.path.join(

        MODEL_DIR,

        "feature_names.npy"

    ),

    np.array(
        feature_names
    )

)


# ============================================================
# 30. SAVE MODEL METADATA
# ============================================================

model_info = {

    "model":
        "XGBoost",

    "task":
        "Cosmetic Ingredient Conflict Risk Prediction",

    "classes":
        [
            "Safe",
            "Medium Risk",
            "High Risk"
        ],

    "accuracy":
        float(
            accuracy
        ),

    "balanced_accuracy":
        float(
            balanced_accuracy
        ),

    "macro_precision":
        float(
            macro_precision
        ),

    "macro_recall":
        float(
            macro_recall
        ),

    "macro_f1":
        float(
            macro_f1
        ),

    "training_rows":
        int(
            len(X_train)
        ),

    "testing_rows":
        int(
            len(X_test)
        ),

    "features":
        int(
            X_train.shape[1]
        ),

    "tfidf_enabled":
        True,

    "ingredient_identity_features":
        True,

    "canonical_pair_features":
        True,

    "co_occurrence_feature":
        True,

    "external_evidence_enabled":
        True,

    "external_evidence_log_scaled":
        True,

    "external_evidence_indicator":
        True,

    "class_imbalance_handling":
        True,

    "shap_enabled":
        True

}


with open(

    os.path.join(

        MODEL_DIR,

        "model_info.pkl"

    ),

    "wb"

) as f:

    pickle.dump(

        model_info,

        f

    )


# ============================================================
# 31. SHAP EXPLAINABILITY
# ============================================================

print("\n========================================")
print("GENERATING SHAP EXPLANATIONS")
print("========================================")


try:

    # --------------------------------------------------------
    # Use a small background set because permutation SHAP can
    # be expensive with many TF-IDF features.
    # --------------------------------------------------------

    background_size = min(
        10,
        len(X_train)
    )


    background_data = (
        X_train[
            :background_size
        ]
    )


    print(
        "SHAP background samples:",
        background_size
    )


    explainer = shap.Explainer(

        model.predict_proba,

        background_data,

        algorithm="permutation"

    )


    sample_size = min(
        10,
        len(X_test)
    )


    X_sample = (
        X_test[
            :sample_size
        ]
    )


    print(
        "SHAP explanation samples:",
        sample_size
    )


    shap_explanation = explainer(
        X_sample
    )


    print(
        "SHAP explanation generated successfully!"
    )


    # --------------------------------------------------------
    # SAVE SHAP VALUES
    # --------------------------------------------------------

    np.save(

        os.path.join(

            MODEL_DIR,

            "shap_values.npy"

        ),

        shap_explanation.values

    )


    print(
        "SHAP values saved."
    )


    # --------------------------------------------------------
    # SAVE BASE VALUES
    # --------------------------------------------------------

    np.save(

        os.path.join(

            MODEL_DIR,

            "shap_base_values.npy"

        ),

        shap_explanation.base_values

    )


    print(
        "SHAP base values saved."
    )


except Exception as e:

    print(
        "\nSHAP generation failed:"
    )

    print(
        type(e).__name__
    )

    print(
        str(e)
    )

    raise


# ============================================================
# 32. TEST KNOWN HIGH-RISK PAIRS
# ============================================================

print("\n========================================")
print("TESTING KNOWN HIGH-RISK COMBINATIONS")
print("========================================")


known_high_risk_pairs = [

    (
        "retinol",
        "benzoyl peroxide"
    ),

    (
        "retinol",
        "salicylic acid"
    ),

    (
        "retinol",
        "glycolic acid"
    ),

    (
        "retinol",
        "lactic acid"
    ),

    (
        "retinol",
        "mandelic acid"
    ),

    (
        "retinol",
        "azelaic acid"
    ),

    (
        "benzoyl peroxide",
        "salicylic acid"
    ),

    (
        "benzoyl peroxide",
        "glycolic acid"
    ),

    (
        "salicylic acid",
        "glycolic acid"
    ),

    (
        "salicylic acid",
        "lactic acid"
    ),

    (
        "ascorbic acid",
        "benzoyl peroxide"
    ),

    (
        "vitamin c",
        "benzoyl peroxide"
    ),

    (
        "retinol",
        "vitamin c"
    ),

    (
        "retinol",
        "ascorbic acid"
    ),

    (
        "aha",
        "retinol"
    ),

    (
        "bha",
        "retinol"
    ),

    (
        "tretinoin",
        "benzoyl peroxide"
    ),

    (
        "tretinoin",
        "salicylic acid"
    )

]


def create_model_text(
    ingredient_a,
    ingredient_b
):

    ingredient_a = clean_ingredient(
        ingredient_a
    )

    ingredient_b = clean_ingredient(
        ingredient_b
    )

    token_a = ingredient_token(
        ingredient_a
    )

    token_b = ingredient_token(
        ingredient_b
    )

    canonical_pair = "||".join(

        sorted([
            ingredient_a,
            ingredient_b
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
        + token_a

        + " "

        + "ING2_"
        + token_b

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


test_texts = [

    create_model_text(
        a,
        b
    )

    for a, b
    in known_high_risk_pairs

]


test_text_features = (

    vectorizer
    .transform(
        test_texts
    )
    .toarray()

)


# ------------------------------------------------------------
# For unknown test pairs, external evidence is loaded again.
# ------------------------------------------------------------

test_internal_features = []
test_external_features = []
test_external_indicators = []


for ingredient_a, ingredient_b in known_high_risk_pairs:

    internal_value = 0.0

    try:

        external_value = (
            get_external_co_occurrence(

                clean_ingredient(
                    ingredient_a
                ),

                clean_ingredient(
                    ingredient_b
                ),

                external_df

            )
        )

    except Exception:

        external_value = 0.0


    test_internal_features.append(
        np.log1p(
            internal_value
        )
    )


    test_external_features.append(
        np.log1p(
            external_value
        )
    )


    test_external_indicators.append(

        1.0
        if external_value > 0
        else 0.0

    )


test_internal_features = np.array(

    test_internal_features

).reshape(
    -1,
    1
)


test_external_features = np.array(

    test_external_features

).reshape(
    -1,
    1
)


test_external_indicators = np.array(

    test_external_indicators

).reshape(
    -1,
    1
)


X_known_high_risk = np.hstack([

    test_text_features,

    test_internal_features,

    test_external_features,

    test_external_indicators

])


known_predictions = model.predict(
    X_known_high_risk
)


known_probabilities = model.predict_proba(
    X_known_high_risk
)


print()


for i, (
    ingredient_a,
    ingredient_b
) in enumerate(
    known_high_risk_pairs
):

    prediction_id = int(
        known_predictions[i]
    )


    if prediction_id == 0:

        prediction = "Safe"

    elif prediction_id == 1:

        prediction = "Medium Risk"

    else:

        prediction = "High Risk"


    probabilities = (
        known_probabilities[i]
    )


    print(
        f"{ingredient_a} + {ingredient_b}"
    )


    print(
        f"Prediction: {prediction}"
    )


    print(
        f"Safe:        {probabilities[0]:.4f}"
    )


    print(
        f"Medium Risk: {probabilities[1]:.4f}"
    )


    print(
        f"High Risk:   {probabilities[2]:.4f}"
    )


    print("-" * 50)


# ============================================================
# 33. HIGH-RISK TEST SUMMARY
# ============================================================

high_risk_predictions = (

    known_predictions == 2

).sum()


total_high_risk_tests = (
    len(known_high_risk_pairs)
)


print("\n========================================")
print("HIGH-RISK TEST SUMMARY")
print("========================================")


print(
    "Known High Risk pairs tested:",
    total_high_risk_tests
)


print(
    "Predicted High Risk:",
    int(
        high_risk_predictions
    )
)


print(
    "High Risk recognition:",
    round(

        (
            high_risk_predictions
            / total_high_risk_tests
        )
        * 100,

        2

    ),
    "%"
)


# ============================================================
# 34. FINAL OUTPUT
# ============================================================

print("\n========================================")
print("MEMBER 3 ML PIPELINE COMPLETED")
print("========================================")


print("\nGenerated files:")


print(
    "1. ml/model/xgboost_risk_model.json"
)


print(
    "2. ml/model/tfidf_vectorizer.pkl"
)


print(
    "3. ml/model/risk_classes.npy"
)


print(
    "4. ml/model/feature_names.npy"
)


print(
    "5. ml/model/shap_values.npy"
)


print(
    "6. ml/model/shap_base_values.npy"
)


print(
    "7. ml/model/model_info.pkl"
)


print("\n========================================")
print("XGBOOST + EXTERNAL EVIDENCE + SHAP")
print("COMPLETED SUCCESSFULLY")
print("========================================")

