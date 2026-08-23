import pandas as pd
from pathlib import Path

# ============================================================
# COSMETIC INGREDIENT CONFLICT DATASET - CLEANING
# ============================================================

INPUT_FILE = Path("data/ingredient_pairs_3000_severity.xlsx")
OUTPUT_FILE = Path("data/clean_dataset.csv")


print("\n========== DATA CLEANING STARTED ==========\n")

# ------------------------------------------------------------
# 1. Check input file
# ------------------------------------------------------------

if not INPUT_FILE.exists():
    print("ERROR: Dataset file not found!")
    print("Expected:", INPUT_FILE)
    exit()

# ------------------------------------------------------------
# 2. Read Excel dataset
# ------------------------------------------------------------

df = pd.read_excel(INPUT_FILE)

print("Original number of rows:", len(df))
print("Original number of columns:", len(df.columns))

# ------------------------------------------------------------
# 3. Standardize column names
# ------------------------------------------------------------

df.columns = df.columns.str.strip()

expected_columns = [
    "Ingredient_1",
    "Ingredient_2",
    "Co_Occurrence_Count",
    "Severity",
    "Severity_Note"
]

missing_columns = [
    column for column in expected_columns
    if column not in df.columns
]

if missing_columns:
    print("\nERROR: Missing expected columns:")
    print(missing_columns)
    exit()

# ------------------------------------------------------------
# 4. Clean ingredient names
# ------------------------------------------------------------

df["Ingredient_1"] = (
    df["Ingredient_1"]
    .astype(str)
    .str.strip()
)

df["Ingredient_2"] = (
    df["Ingredient_2"]
    .astype(str)
    .str.strip()
)

# ------------------------------------------------------------
# 5. Clean severity labels
# ------------------------------------------------------------

df["Severity"] = (
    df["Severity"]
    .astype(str)
    .str.strip()
)

# Standardize known labels
severity_mapping = {
    "safe": "Safe",
    "medium risk": "Medium Risk",
    "high risk": "High Risk"
}

df["Severity"] = (
    df["Severity"]
    .str.lower()
    .map(severity_mapping)
)

# ------------------------------------------------------------
# 6. Clean severity notes
# ------------------------------------------------------------

df["Severity_Note"] = (
    df["Severity_Note"]
    .astype(str)
    .str.strip()
)

# ------------------------------------------------------------
# 7. Clean co-occurrence count
# ------------------------------------------------------------

df["Co_Occurrence_Count"] = pd.to_numeric(
    df["Co_Occurrence_Count"],
    errors="coerce"
)

# ------------------------------------------------------------
# 8. Remove rows with invalid/missing essential data
# ------------------------------------------------------------

before_cleaning = len(df)

df = df.dropna(
    subset=[
        "Ingredient_1",
        "Ingredient_2",
        "Co_Occurrence_Count",
        "Severity"
    ]
)

after_cleaning = len(df)

print("\nRows removed because of invalid essential data:",
      before_cleaning - after_cleaning)

# ------------------------------------------------------------
# 9. Remove exact duplicate rows
# ------------------------------------------------------------

duplicates_before = df.duplicated().sum()

df = df.drop_duplicates()

print("Duplicate rows removed:", duplicates_before)

# ------------------------------------------------------------
# 10. Validate severity labels
# ------------------------------------------------------------

valid_severities = {
    "Safe",
    "Medium Risk",
    "High Risk"
}

invalid_severities = set(df["Severity"].unique()) - valid_severities

if invalid_severities:
    print("\nWARNING: Unexpected severity labels:")
    print(invalid_severities)
else:
    print("\nSeverity labels are valid.")

# ------------------------------------------------------------
# 11. Sort data for consistency
# ------------------------------------------------------------

df = df.sort_values(
    by=["Severity", "Ingredient_1", "Ingredient_2"]
).reset_index(drop=True)

# ------------------------------------------------------------
# 12. Save cleaned dataset
# ------------------------------------------------------------

df.to_csv(
    OUTPUT_FILE,
    index=False,
    encoding="utf-8"
)

# ------------------------------------------------------------
# 13. Final report
# ------------------------------------------------------------

print("\n========== CLEANING COMPLETE ==========\n")

print("Final number of rows:", len(df))
print("Final number of columns:", len(df.columns))

print("\nFinal columns:")
for column in df.columns:
    print("-", column)

print("\nFinal missing values:")
print(df.isnull().sum())

print("\nFinal duplicate rows:", df.duplicated().sum())

print("\nFinal severity distribution:")
print(df["Severity"].value_counts())

print("\nClean dataset saved to:")
print(OUTPUT_FILE)

print("\n========================================\n")