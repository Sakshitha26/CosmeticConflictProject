import pandas as pd
from pathlib import Path

# ==============================
# FILE PATHS
# ==============================

BASE_DIR = Path(__file__).resolve().parent.parent

dataset_path = BASE_DIR / "data" / "normalized_dataset.csv"
properties_path = BASE_DIR / "data" / "ingredient_properties.csv"
output_path = BASE_DIR / "data" / "ml_ready_dataset.csv"


# ==============================
# LOAD DATA
# ==============================

df = pd.read_csv(dataset_path)
properties = pd.read_csv(properties_path)

print("FEATURE ENGINEERING STARTED")
print("Dataset rows:", len(df))
print("Properties rows:", len(properties))


# ==============================
# CLEAN INGREDIENT NAMES
# ==============================

df["Ingredient_1"] = df["Ingredient_1"].astype(str).str.strip()
df["Ingredient_2"] = df["Ingredient_2"].astype(str).str.strip()

properties["ingredient"] = (
    properties["ingredient"]
    .astype(str)
    .str.strip()
)


# ==============================
# PROPERTY COLUMNS
# ==============================

property_columns = [
    "exfoliant",
    "retinoid",
    "antioxidant",
    "drying_agent",
    "humectant",
    "emollient",
    "preservative",
    "fragrance",
    "active_ingredient"
]


# ==============================
# CREATE LOOKUP TABLE
# ==============================

properties_lookup = properties.set_index("ingredient")


# ==============================
# GET PROPERTIES FOR INGREDIENT 1
# ==============================

for column in property_columns:
    df[f"A_{column}"] = (
        df["Ingredient_1"]
        .map(properties_lookup[column])
        .fillna(0)
    )


# ==============================
# GET PROPERTIES FOR INGREDIENT 2
# ==============================

for column in property_columns:
    df[f"B_{column}"] = (
        df["Ingredient_2"]
        .map(properties_lookup[column])
        .fillna(0)
    )


# ==============================
# CREATE COMBINED FEATURES
# ==============================

for column in property_columns:

    df[f"sum_{column}"] = (
        df[f"A_{column}"] +
        df[f"B_{column}"]
    )

    df[f"difference_{column}"] = (
        abs(
            df[f"A_{column}"] -
            df[f"B_{column}"]
        )
    )


# ==============================
# CO-OCCURRENCE FEATURE
# ==============================

if "Co_Occurrence_Count" in df.columns:
    df["co_occurrence"] = pd.to_numeric(
        df["Co_Occurrence_Count"],
        errors="coerce"
    ).fillna(0)
else:
    df["co_occurrence"] = 0


# ==============================
# TARGET LABEL
# ==============================

if "Severity" in df.columns:
    df["target"] = df["Severity"].astype(str).str.strip()
else:
    raise ValueError("Severity column not found in dataset")


# ==============================
# SAVE ML DATASET
# ==============================

df.to_csv(output_path, index=False)


# ==============================
# RESULTS
# ==============================

print()
print("FEATURE ENGINEERING COMPLETE")
print("Total rows:", len(df))
print("Total columns:", len(df.columns))
print("Saved to:", output_path)

print()
print("Target distribution:")
print(df["target"].value_counts())

print()
print("First 5 rows:")
print(df.head().to_string(index=False))