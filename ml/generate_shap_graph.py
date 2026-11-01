import os
import ast
import numpy as np
import matplotlib.pyplot as plt


# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

MODEL_DIR = os.path.join(BASE_DIR, "ml", "model")

SHAP_FILE = os.path.join(MODEL_DIR, "shap_values.npy")
FEATURE_FILE = os.path.join(MODEL_DIR, "feature_names.npy")

OUTPUT_FILE = os.path.join(
    MODEL_DIR,
    "shap_feature_importance.png"
)


# ============================================================
# LOAD SHAP VALUES
# ============================================================

print("Loading SHAP values...")

shap_raw = np.load(
    SHAP_FILE,
    allow_pickle=True
)

print("Original SHAP shape:", shap_raw.shape)


# ============================================================
# CONVERT SHAP DATA TO NUMERIC
# ============================================================

def convert_to_array(value):

    if isinstance(value, np.ndarray):
        return value.astype(float)

    if isinstance(value, (list, tuple)):
        return np.asarray(value, dtype=float)

    if isinstance(value, str):

        value = value.strip()

        try:
            parsed = ast.literal_eval(value)
            return np.asarray(parsed, dtype=float)

        except Exception:

            cleaned = value.strip("[]")

            values = [
                float(x)
                for x in cleaned.replace(",", " ").split()
            ]

            return np.asarray(values, dtype=float)

    return np.asarray(value, dtype=float)


# ============================================================
# PROCESS SHAP VALUES
# ============================================================

arrays = []

for item in shap_raw:

    try:
        arr = convert_to_array(item)

        if arr.ndim == 1:
            arrays.append(arr)

    except Exception as e:
        print("Skipping invalid SHAP value:", e)


if len(arrays) == 0:
    raise ValueError(
        "Could not convert SHAP values into numeric arrays."
    )


shap_matrix = np.vstack(arrays)

print("Converted SHAP shape:", shap_matrix.shape)


# ============================================================
# LOAD FEATURE NAMES
# ============================================================

feature_names = np.load(
    FEATURE_FILE,
    allow_pickle=True
)

feature_names = np.asarray(
    feature_names,
    dtype=str
)

print("Number of features:", len(feature_names))


# ============================================================
# FIX FEATURE COUNT IF NECESSARY
# ============================================================

num_features = min(
    shap_matrix.shape[1],
    len(feature_names)
)

shap_matrix = shap_matrix[:, :num_features]
feature_names = feature_names[:num_features]


# ============================================================
# CALCULATE MEAN ABSOLUTE SHAP
# ============================================================

mean_abs_shap = np.mean(
    np.abs(shap_matrix),
    axis=0
)


# ============================================================
# TOP 15 FEATURES
# ============================================================

top_indices = np.argsort(
    mean_abs_shap
)[-15:][::-1]

top_features = feature_names[top_indices]

top_values = mean_abs_shap[top_indices]


# ============================================================
# PRINT RESULTS
# ============================================================

print("\nTop SHAP Features:")
print("-" * 50)

for feature, value in zip(
    top_features,
    top_values
):
    print(
        f"{feature:<40} {value:.6f}"
    )


# ============================================================
# CREATE GRAPH
# ============================================================

plt.figure(figsize=(10, 7))

plt.barh(
    range(len(top_features)),
    top_values[::-1]
)

plt.yticks(
    range(len(top_features)),
    top_features[::-1]
)

plt.xlabel(
    "Mean Absolute SHAP Value"
)

plt.ylabel(
    "Feature"
)

plt.title(
    "Top 15 Features - SHAP Feature Importance"
)

plt.tight_layout()


# ============================================================
# SAVE GRAPH
# ============================================================

plt.savefig(
    OUTPUT_FILE,
    dpi=300,
    bbox_inches="tight"
)

plt.close()

print("\nSHAP graph generated successfully!")

print(
    "\nSaved at:"
)

print(OUTPUT_FILE)