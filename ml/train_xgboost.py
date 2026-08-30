import os
import pickle
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
    f1_score
)
from sklearn.utils.class_weight import compute_sample_weight

from xgboost import XGBClassifier


# ============================================================
# 1. PATHS
# ============================================================

DATA_PATH = "data/ingredient_pairs_3000_severity.xlsx"
MODEL_DIR = "ml/model"

os.makedirs(MODEL_DIR, exist_ok=True)


# ============================================================
# 2. LOAD DATASET
# ============================================================

print("\n========================================")
print("LOADING COSMETIC CONFLICT DATASET")
print("========================================")

df = pd.read_excel(DATA_PATH)

print("Dataset loaded successfully!")
print("Rows:", len(df))
print("Columns:", df.columns.tolist())


# ============================================================
# 3. CHECK REQUIRED COLUMNS
# ============================================================

required_columns = [
    "Ingredient_1",
    "Ingredient_2",
    "Co_Occurrence_Count",
    "Severity"
]

missing_columns = [
    col for col in required_columns
    if col not in df.columns
]

if missing_columns:
    raise ValueError(
        f"Missing required columns: {missing_columns}"
    )


# ============================================================
# 4. CLEAN DATA
# ============================================================

print("\nCleaning dataset...")

df = df.dropna(
    subset=required_columns
).copy()

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
    "medium risk": 1,
    "high risk": 2
}

df = df[
    df["Severity"].isin(
        risk_mapping.keys()
    )
].copy()

# Remove duplicate pairs
df = df.drop_duplicates(
    subset=[
        "Ingredient_1",
        "Ingredient_2"
    ]
)

print(
    "Rows after cleaning:",
    len(df)
)


# ============================================================
# 6. DISPLAY CLASS DISTRIBUTION
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
    distribution.get("safe", 0)
)

print(
    "Medium Risk:",
    distribution.get("medium risk", 0)
)

print(
    "High Risk:",
    distribution.get("high risk", 0)
)


# ============================================================
# 7. CREATE INGREDIENT PAIR
# ============================================================

df["Ingredient_Pair"] = (
    df["Ingredient_1"]
    + " "
    + df["Ingredient_2"]
)


# ============================================================
# 8. CREATE TARGET
# ============================================================

df["Risk_Label"] = df["Severity"].map(
    risk_mapping
)

y = df["Risk_Label"].values


print("\nRisk mapping:")
print("0 = Safe")
print("1 = Medium Risk")
print("2 = High Risk")


# ============================================================
# 9. TRAIN / TEST SPLIT
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
    count_test
) = train_test_split(
    df["Ingredient_Pair"],
    y,
    df["Co_Occurrence_Count"].values,
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
# 10. TF-IDF
# ============================================================

print("\n========================================")
print("CREATING TF-IDF FEATURES")
print("========================================")

vectorizer = TfidfVectorizer(
    ngram_range=(1, 2),
    min_df=1
)

X_train_text = vectorizer.fit_transform(
    text_train
).toarray()

X_test_text = vectorizer.transform(
    text_test
).toarray()


# ============================================================
# 11. ADD CO-OCCURRENCE FEATURE
# ============================================================

X_train = np.hstack([
    X_train_text,
    count_train.reshape(-1, 1)
])

X_test = np.hstack([
    X_test_text,
    count_test.reshape(-1, 1)
])


print(
    "Training feature shape:",
    X_train.shape
)

print(
    "Testing feature shape:",
    X_test.shape
)


# ============================================================
# 12. HANDLE CLASS IMBALANCE
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
    round(float(sample_weights.min()), 4)
)

print(
    "Maximum weight:",
    round(float(sample_weights.max()), 4)
)


# ============================================================
# 13. TRAIN XGBOOST
# ============================================================

print("\n========================================")
print("TRAINING XGBOOST")
print("========================================")

model = XGBClassifier(
    n_estimators=250,
    max_depth=5,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    objective="multi:softprob",
    num_class=3,
    eval_metric="mlogloss",
    random_state=42
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
# 14. PREDICTION
# ============================================================

print("\nMaking predictions...")

y_pred = model.predict(
    X_test
)


# ============================================================
# 15. BASIC METRICS
# ============================================================

accuracy = accuracy_score(
    y_test,
    y_pred
)

balanced_accuracy = balanced_accuracy_score(
    y_test,
    y_pred
)

macro_f1 = f1_score(
    y_test,
    y_pred,
    average="macro",
    zero_division=0
)


# ============================================================
# 16. MODEL RESULTS
# ============================================================

print("\n========================================")
print("XGBOOST MODEL RESULTS")
print("========================================")

print(
    "Accuracy:",
    round(accuracy * 100, 2),
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
    "Macro F1:",
    round(
        macro_f1,
        4
    )
)


# ============================================================
# 17. CLASSIFICATION REPORT
# ============================================================

print("\nClassification Report:")

print(
    classification_report(
        y_test,
        y_pred,
        labels=[0, 1, 2],
        target_names=[
            "Safe",
            "Medium Risk",
            "High Risk"
        ],
        zero_division=0
    )
)


# ============================================================
# 18. CONFUSION MATRIX
# ============================================================

print("\nConfusion Matrix:")

cm = confusion_matrix(
    y_test,
    y_pred,
    labels=[0, 1, 2]
)

print(
    pd.DataFrame(
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
)


# ============================================================
# 19. SAVE XGBOOST MODEL
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

print(model_path)


# ============================================================
# 20. SAVE TF-IDF VECTORIZER
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

print(vectorizer_path)


# ============================================================
# 21. SAVE RISK CLASSES
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
# 22. SAVE FEATURE NAMES
# ============================================================

feature_names = list(
    vectorizer.get_feature_names_out()
)

feature_names.append(
    "Co_Occurrence_Count"
)

np.save(
    os.path.join(
        MODEL_DIR,
        "feature_names.npy"
    ),
    np.array(feature_names)
)


# ============================================================
# 23. SHAP EXPLAINABILITY
# ============================================================

print("\n========================================")
print("GENERATING SHAP EXPLANATIONS")
print("========================================")

try:

    # SHAP 0.46.0 + XGBoost 3.4.x can have
    # TreeExplainer compatibility issues for
    # multiclass models.
    #
    # Therefore we use the generic SHAP
    # PermutationExplainer.

    background_size = min(
        20,
        len(X_train)
    )

    background_data = X_train[
        :background_size
    ]

    explainer = shap.Explainer(
        model.predict_proba,
        background_data,
        algorithm="permutation"
    )

    sample_size = min(
        50,
        len(X_test)
    )

    X_sample = X_test[
        :sample_size
    ]

    shap_explanation = explainer(
        X_sample
    )

    print(
        "SHAP explanation generated successfully!"
    )


    # ========================================================
    # 24. SAVE SHAP VALUES
    # ========================================================

    shap_values = shap_explanation.values

    np.save(
        os.path.join(
            MODEL_DIR,
            "shap_values.npy"
        ),
        shap_values
    )

    print(
        "SHAP values saved."
    )


    # ========================================================
    # 25. SAVE SHAP BASE VALUES
    # ========================================================

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
# 26. SAVE MODEL INFORMATION
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
        float(accuracy),

    "balanced_accuracy":
        float(balanced_accuracy),

    "macro_f1":
        float(macro_f1),

    "training_rows":
        int(len(X_train)),

    "testing_rows":
        int(len(X_test)),

    "features":
        int(X_train.shape[1]),

    "tfidf_enabled":
        True,

    "co_occurrence_feature":
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
# 27. FINAL OUTPUT
# ============================================================

print("\n========================================")
print("MEMBER 3 ML PIPELINE COMPLETED")
print("========================================")

print("\nFiles created:")

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
print("XGBOOST + SHAP COMPLETED SUCCESSFULLY")
print("========================================")