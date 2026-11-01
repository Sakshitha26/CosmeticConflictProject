
import os
import pickle
import re
import warnings

import numpy as np
import pandas as pd
import shap
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    classification_report,
    confusion_matrix,
    ConfusionMatrixDisplay,
    f1_score,
    precision_score,
    recall_score
)

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

os.makedirs(
    MODEL_DIR,
    exist_ok=True
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

SHAP_VALUES_PATH = os.path.join(
    MODEL_DIR,
    "shap_values.npy"
)

SHAP_BASE_VALUES_PATH = os.path.join(
    MODEL_DIR,
    "shap_base_values.npy"
)

MODEL_INFO_PATH = os.path.join(
    MODEL_DIR,
    "model_info.pkl"
)

CONFUSION_MATRIX_CSV = os.path.join(
    MODEL_DIR,
    "confusion_matrix.csv"
)

CONFUSION_MATRIX_PNG = os.path.join(
    MODEL_DIR,
    "confusion_matrix.png"
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
# 4. CREATE MODEL TEXT
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
# 5. LOAD DATASET
# ============================================================

print("\n========================================")
print("LOADING TRAINING DATA")
print("========================================")


if not os.path.exists(DATA_PATH):

    raise FileNotFoundError(
        f"Dataset not found:\n{DATA_PATH}"
    )


df = pd.read_excel(
    DATA_PATH
)


print(
    "Dataset loaded successfully!"
)

print(
    "Rows:",
    len(df)
)

print(
    "Columns:",
    df.columns.tolist()
)


# ============================================================
# 6. NORMALIZE COLUMN NAMES
# ============================================================

df.columns = (
    df.columns
    .astype(str)
    .str.strip()
)


# Accept either spelling of severity explanation
if (
    "Severity Explanation" not in df.columns
    and
    "Severity_Explanation" in df.columns
):

    df.rename(
        columns={
            "Severity_Explanation":
            "Severity Explanation"
        },
        inplace=True
    )


# ============================================================
# 7. REQUIRED COLUMNS
# ============================================================

required_columns = [
    "Ingredient_A",
    "Ingredient_B",
    "Severity",
    "Severity Explanation"
]


missing_columns = [
    column
    for column in required_columns
    if column not in df.columns
]


if missing_columns:

    raise ValueError(
        "\nMissing required dataset columns:\n"
        + "\n".join(missing_columns)
        + "\n\nAvailable columns:\n"
        + str(df.columns.tolist())
    )


# ============================================================
# 8. CLEAN DATA
# ============================================================

df["Ingredient_A"] = (
    df["Ingredient_A"]
    .apply(clean_ingredient)
)

df["Ingredient_B"] = (
    df["Ingredient_B"]
    .apply(clean_ingredient)
)


df["Severity"] = (
    df["Severity"]
    .astype(str)
    .str.lower()
    .str.strip()
)


# ============================================================
# 9. REMOVE EMPTY ROWS
# ============================================================

df = df[
    (df["Ingredient_A"] != "")
    &
    (df["Ingredient_B"] != "")
    &
    (df["Severity"] != "")
]


df = df.reset_index(
    drop=True
)


# ============================================================
# 10. CONVERT SEVERITY LABELS
# ============================================================

severity_mapping = {

    "safe": 0,

    "low": 0,

    "medium": 1,

    "medium risk": 1,

    "high": 2,

    "high risk": 2

}


df["Severity_Label"] = (
    df["Severity"]
    .map(severity_mapping)
)


# ============================================================
# 11. CHECK INVALID LABELS
# ============================================================

invalid_labels = df[
    df["Severity_Label"].isna()
]["Severity"].unique()


if len(invalid_labels) > 0:

    raise ValueError(
        "\nUnknown severity labels found:\n"
        + str(invalid_labels)
        + "\n\nExpected labels:\n"
        + str(list(severity_mapping.keys()))
    )


df["Severity_Label"] = (
    df["Severity_Label"]
    .astype(int)
)


# ============================================================
# 12. DATASET SUMMARY
# ============================================================

print("\n========================================")
print("DATASET SUMMARY")
print("========================================")

print(
    "Total samples:",
    len(df)
)

print(
    "\nClass distribution:"
)

print(
    df["Severity_Label"]
    .value_counts()
    .sort_index()
)


# ============================================================
# 13. CREATE TEXT FEATURES
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


# ============================================================
# 14. TRAIN / TEST SPLIT
# ============================================================

X_text = df["Model_Text"]

y = df["Severity_Label"]


X_train_text, X_test_text, y_train, y_test = (
    train_test_split(
        X_text,
        y,
        test_size=0.20,
        random_state=42,
        stratify=y
    )
)


print(
    "\nTraining samples:",
    len(X_train_text)
)

print(
    "Testing samples:",
    len(X_test_text)
)


# ============================================================
# 15. TF-IDF
# ============================================================

vectorizer = TfidfVectorizer(
    lowercase=False,
    token_pattern=r"(?u)\b[A-Za-z0-9_]+\b",
    ngram_range=(1, 2),
    min_df=1
)


X_train_text_tfidf = (
    vectorizer
    .fit_transform(
        X_train_text
    )
    .toarray()
)


X_test_text_tfidf = (
    vectorizer
    .transform(
        X_test_text
    )
    .toarray()
)


# ============================================================
# 16. EXTERNAL EVIDENCE FEATURES
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
        "External evidence unavailable."
    )

    print(
        "Error:",
        str(e)
    )

    external_df = None

    EXTERNAL_EVIDENCE_AVAILABLE = False


# ============================================================
# 17. EXTERNAL FEATURE CALCULATION
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

        return float(value)

    except Exception:

        return 0.0


def create_external_features(
    data_frame
):

    external_logs = []
    external_indicators = []

    for _, row in data_frame.iterrows():

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

    return (
        np.array(
            external_logs
        ).reshape(-1, 1),
        np.array(
            external_indicators
        ).reshape(-1, 1)
    )


# ============================================================
# 18. CREATE TRAINING EXTERNAL FEATURES
# ============================================================

train_indices = X_train_text.index

test_indices = X_test_text.index


train_df = df.loc[
    train_indices
].copy()


test_df = df.loc[
    test_indices
].copy()


X_train_external_log, X_train_external_indicator = (
    create_external_features(
        train_df
    )
)


X_test_external_log, X_test_external_indicator = (
    create_external_features(
        test_df
    )
)


# ============================================================
# 19. FINAL FEATURES
# ============================================================

X_train = np.hstack([

    X_train_text_tfidf,

    X_train_external_log,

    X_train_external_indicator

])


X_test = np.hstack([

    X_test_text_tfidf,

    X_test_external_log,

    X_test_external_indicator

])


print(
    "\nTraining feature shape:",
    X_train.shape
)

print(
    "Testing feature shape:",
    X_test.shape
)


# ============================================================
# 20. FEATURE NAMES
# ============================================================

tfidf_feature_names = (
    vectorizer
    .get_feature_names_out()
)


feature_names = np.concatenate([

    tfidf_feature_names,

    [
        "External_Co_Occurrence_Log",
        "External_Evidence_Indicator"
    ]

])


# ============================================================
# 21. TRAIN XGBOOST
# ============================================================

print("\n========================================")
print("TRAINING XGBOOST MODEL")
print("========================================")


model = XGBClassifier(

    objective="multi:softprob",

    num_class=3,

    n_estimators=300,

    max_depth=6,

    learning_rate=0.05,

    subsample=0.9,

    colsample_bytree=0.9,

    random_state=42,

    eval_metric="mlogloss"
)


model.fit(
    X_train,
    y_train
)


print(
    "XGBoost training completed!"
)


# ============================================================
# 22. PREDICTION
# ============================================================

print("\n========================================")
print("EVALUATING MODEL")
print("========================================")


y_pred = (
    model
    .predict(
        X_test
    )
)


y_pred = y_pred.astype(int)


# ============================================================
# 23. METRICS
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

precision = precision_score(
    y_test,
    y_pred,
    average="weighted",
    zero_division=0
)

recall = recall_score(
    y_test,
    y_pred,
    average="weighted",
    zero_division=0
)

f1 = f1_score(
    y_test,
    y_pred,
    average="weighted",
    zero_division=0
)


print(
    "\nAccuracy:",
    f"{accuracy * 100:.2f}%"
)

print(
    "Balanced Accuracy:",
    f"{balanced_accuracy * 100:.2f}%"
)

print(
    "Precision:",
    f"{precision * 100:.2f}%"
)

print(
    "Recall:",
    f"{recall * 100:.2f}%"
)

print(
    "F1 Score:",
    f"{f1 * 100:.2f}%"
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
        labels=[0, 1, 2],
        target_names=RISK_CLASSES,
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
    labels=[0, 1, 2]
)


cm_df = pd.DataFrame(
    cm,
    index=RISK_CLASSES,
    columns=RISK_CLASSES
)


cm_df.to_csv(
    CONFUSION_MATRIX_CSV
)


print(
    cm_df
)


# ============================================================
# 26. SAVE CONFUSION MATRIX IMAGE
# ============================================================

disp = ConfusionMatrixDisplay(
    confusion_matrix=cm,
    display_labels=RISK_CLASSES
)


fig, ax = plt.subplots(
    figsize=(8, 6)
)


disp.plot(
    ax=ax,
    values_format="d"
)


plt.title(
    "XGBoost Cosmetic Risk Confusion Matrix"
)

plt.tight_layout()


plt.savefig(
    CONFUSION_MATRIX_PNG,
    dpi=300,
    bbox_inches="tight"
)


plt.close()


print(
    "\nConfusion matrix saved:"
)

print(
    CONFUSION_MATRIX_PNG
)


# ============================================================
# 27. SAVE MODEL
# ============================================================

print("\n========================================")
print("SAVING MODEL")
print("========================================")


model.save_model(
    MODEL_PATH
)


print(
    "XGBoost model saved!"
)


# ============================================================
# 28. SAVE TF-IDF
# ============================================================

with open(
    VECTORIZER_PATH,
    "wb"
) as f:

    pickle.dump(
        vectorizer,
        f
    )


print(
    "TF-IDF vectorizer saved!"
)


# ============================================================
# 29. SAVE RISK CLASSES
# ============================================================

np.save(
    RISK_CLASSES_PATH,
    np.array(
        RISK_CLASSES,
        dtype=object
    )
)


# ============================================================
# 30. SAVE FEATURE NAMES
# ============================================================

np.save(
    FEATURE_NAMES_PATH,
    feature_names
)


# ============================================================
# 31. SHAP EXPLANATION
# ============================================================

print("\n========================================")
print("GENERATING SHAP VALUES")
print("========================================")


try:

    # Use a small sample for faster SHAP calculation
    shap_sample_size = min(
        100,
        len(X_test)
    )

    X_shap = X_test[
        :shap_sample_size
    ]

    explainer = shap.TreeExplainer(
        model
    )

    shap_explanation = (
        explainer(
            X_shap
        )
    )

    shap_values = (
        shap_explanation.values
    )

    base_values = (
        shap_explanation.base_values
    )

    np.save(
        SHAP_VALUES_PATH,
        shap_values
    )

    np.save(
        SHAP_BASE_VALUES_PATH,
        base_values
    )

    print(
        "SHAP values saved!"
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


# ============================================================
# 32. SAVE MODEL INFORMATION
# ============================================================

model_info = {

    "dataset": DATA_PATH,

    "total_samples": len(df),

    "training_samples": len(X_train),

    "testing_samples": len(X_test),

    "feature_count": X_train.shape[1],

    "accuracy": accuracy,

    "balanced_accuracy": balanced_accuracy,

    "precision": precision,

    "recall": recall,

    "f1_score": f1,

    "risk_classes": RISK_CLASSES,

    "co_occurrence_used": False,

    "external_evidence_used":
        EXTERNAL_EVIDENCE_AVAILABLE

}


with open(
    MODEL_INFO_PATH,
    "wb"
) as f:

    pickle.dump(
        model_info,
        f
    )


# ============================================================
# 33. FINAL OUTPUT
# ============================================================

print("\n========================================")
print("TRAINING COMPLETED SUCCESSFULLY")
print("========================================")


print(
    "\nGenerated files:"
)

print(
    "1.",
    MODEL_PATH
)

print(
    "2.",
    VECTORIZER_PATH
)

print(
    "3.",
    RISK_CLASSES_PATH
)

print(
    "4.",
    FEATURE_NAMES_PATH
)

print(
    "5.",
    SHAP_VALUES_PATH
)

print(
    "6.",
    SHAP_BASE_VALUES_PATH
)

print(
    "7.",
    MODEL_INFO_PATH
)

print(
    "8.",
    CONFUSION_MATRIX_CSV
)

print(
    "9.",
    CONFUSION_MATRIX_PNG
)


print(
    "\n========================================"
)

print(
    "XGBOOST + EXTERNAL EVIDENCE + SHAP"
)

print(
    "WITHOUT CO-OCCURRENCE COUNT"
)

print(
    "========================================"
)
