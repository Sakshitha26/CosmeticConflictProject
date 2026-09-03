import pandas as pd
from pathlib import Path

# ============================================================
# PATHS
# ============================================================

BASE_FILE = Path("data/ingredient_pairs_3000_severity.xlsx")
EXTERNAL_FILE = Path("data/external_compatibility_pairs.csv")
OUTPUT_FILE = Path("data/ingredient_pairs_augmented.xlsx")


# ============================================================
# LOAD DATA
# ============================================================

print("=" * 60)
print("MERGING COSMETIC COMPATIBILITY DATA")
print("=" * 60)

base = pd.read_excel(BASE_FILE)
external = pd.read_csv(EXTERNAL_FILE)

print("\nOriginal dataset:")
print(base["Severity"].value_counts())

print("\nExternal evidence:")
print(external["Severity"].value_counts())


# ============================================================
# CLEAN COLUMN NAMES
# ============================================================

base.columns = base.columns.str.strip()
external.columns = external.columns.str.strip()

required_columns = [
    "Ingredient_1",
    "Ingredient_2",
    "Severity",
    "Severity_Note"
]

for col in required_columns:
    if col not in base.columns:
        base[col] = ""

    if col not in external.columns:
        external[col] = ""


# ============================================================
# NORMALIZE INGREDIENT NAMES
# ============================================================

def clean_ingredient(x):
    if pd.isna(x):
        return ""

    return (
        str(x)
        .strip()
        .lower()
        .replace("_", " ")
    )


for df in [base, external]:
    df["Ingredient_1"] = df["Ingredient_1"].apply(clean_ingredient)
    df["Ingredient_2"] = df["Ingredient_2"].apply(clean_ingredient)
    df["Severity"] = df["Severity"].astype(str).str.strip()


# ============================================================
# NORMALIZE PAIR ORDER
# ============================================================

def make_pair_key(row):
    ingredients = sorted([
        row["Ingredient_1"],
        row["Ingredient_2"]
    ])

    return ingredients[0] + "||" + ingredients[1]


base["Pair_Key"] = base.apply(make_pair_key, axis=1)
external["Pair_Key"] = external.apply(make_pair_key, axis=1)


# ============================================================
# REMOVE EXTERNAL DUPLICATES
# ============================================================

external = external.drop_duplicates(
    subset=["Pair_Key"],
    keep="first"
)


# ============================================================
# ADD ONLY NEW PAIRS
# ============================================================

existing_pairs = set(base["Pair_Key"])

new_external = external[
    ~external["Pair_Key"].isin(existing_pairs)
].copy()


print("\nExternal pairs already present:", 
      len(external) - len(new_external))

print("New external pairs added:",
      len(new_external))


# ============================================================
# KEEP REQUIRED COLUMNS
# ============================================================

new_external = new_external[
    [
        "Ingredient_1",
        "Ingredient_2",
        "Severity",
        "Severity_Note"
    ]
]


base_clean = base[
    [
        "Ingredient_1",
        "Ingredient_2",
        "Severity",
        "Severity_Note"
    ]
]


# ============================================================
# MERGE
# ============================================================

augmented = pd.concat(
    [base_clean, new_external],
    ignore_index=True
)


# ============================================================
# FINAL CLEANUP
# ============================================================

augmented["Ingredient_1"] = (
    augmented["Ingredient_1"]
    .astype(str)
    .str.strip()
)

augmented["Ingredient_2"] = (
    augmented["Ingredient_2"]
    .astype(str)
    .str.strip()
)

augmented["Severity"] = (
    augmented["Severity"]
    .astype(str)
    .str.strip()
)


# Remove exact duplicates
augmented = augmented.drop_duplicates(
    subset=[
        "Ingredient_1",
        "Ingredient_2"
    ]
)


# ============================================================
# SAVE
# ============================================================

augmented.to_excel(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# REPORT
# ============================================================

print("\n" + "=" * 60)
print("AUGMENTED DATASET CREATED")
print("=" * 60)

print("\nTotal rows:", len(augmented))

print("\nNew class distribution:")
print(augmented["Severity"].value_counts())

print("\nNew percentages:")
print(
    augmented["Severity"]
    .value_counts(normalize=True)
    .mul(100)
    .round(2)
)

print("\nOutput:")
print(OUTPUT_FILE)

print("=" * 60)