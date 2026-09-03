import pandas as pd
import json
import re
from pathlib import Path

# ============================================================
# CONFIG
# ============================================================

EXISTING_DATASET = "data/ingredient_pairs_augmented.xlsx"

# Change these paths if your downloaded external files have
# different names/locations.
BSYILMAZ_INGREDIENTS = "data/external_bsyilmaz_ingredients.json"
BSYILMAZ_RULES = "data/external_bsyilmaz_compatibility_rules.json"

SCANALYZE = "data/external_scanalyze.csv"

CURESKIN = "data/external_cureskin.csv"


# ============================================================
# NORMALIZATION
# ============================================================

def normalize(name):
    if pd.isna(name):
        return ""

    name = str(name).lower().strip()

    name = re.sub(r"\([^)]*\)", "", name)
    name = re.sub(r"[^a-z0-9\s\-]", " ", name)
    name = re.sub(r"\s+", " ", name)

    return name.strip()


def canonical_pair(a, b):
    a = normalize(a)
    b = normalize(b)

    if not a or not b or a == b:
        return None

    return tuple(sorted([a, b]))


# ============================================================
# EXISTING DATASET
# ============================================================

print("=" * 60)
print("DATASET OVERLAP CHECK")
print("=" * 60)

print("\nLoading existing dataset...")

df = pd.read_excel(EXISTING_DATASET)

print(f"Existing rows: {len(df)}")

existing_ingredients = set()

for col in ["Ingredient_1", "Ingredient_2"]:
    if col in df.columns:
        existing_ingredients.update(
            normalize(x)
            for x in df[col]
            if normalize(x)
        )

existing_pairs = set()

for _, row in df.iterrows():
    pair = canonical_pair(
        row["Ingredient_1"],
        row["Ingredient_2"]
    )

    if pair:
        existing_pairs.add(pair)

print(f"Unique existing ingredients: {len(existing_ingredients)}")
print(f"Unique existing pairs: {len(existing_pairs)}")


# ============================================================
# BSYILMAZ
# ============================================================

print("\n" + "-" * 60)
print("BSYILMAZ DATASET")
print("-" * 60)

if Path(BSYILMAZ_INGREDIENTS).exists():

    with open(BSYILMAZ_INGREDIENTS, "r", encoding="utf-8") as f:
        data = json.load(f)

    source_ingredients = set()

    if isinstance(data, dict):
        records = data.values()
    else:
        records = data

    for item in records:
        if isinstance(item, dict):
            for key in [
                "inci_name",
                "common_name",
                "name"
            ]:
                if key in item:
                    value = normalize(item[key])
                    if value:
                        source_ingredients.add(value)

    overlap = source_ingredients & existing_ingredients
    new = source_ingredients - existing_ingredients

    print(f"Source ingredients : {len(source_ingredients)}")
    print(f"Already existing   : {len(overlap)}")
    print(f"New ingredients    : {len(new)}")

    if source_ingredients:
        print(
            f"Overlap percentage: "
            f"{len(overlap) / len(source_ingredients) * 100:.2f}%"
        )

    print("\nNew ingredients:")
    for x in sorted(new):
        print("  ", x)

else:
    print("BSYILMAZ ingredient file not found:")
    print(BSYILMAZ_INGREDIENTS)


# ============================================================
# BSYILMAZ PAIRS
# ============================================================

if Path(BSYILMAZ_RULES).exists():

    with open(BSYILMAZ_RULES, "r", encoding="utf-8") as f:
        rules = json.load(f)

    source_pairs = set()

    # Try to recursively find pair/group information
    def scan(obj):

        if isinstance(obj, dict):

            # Look for ingredient lists/groups
            ingredients = []

            for key in [
                "ingredients",
                "ingredient_group",
                "group",
                "members"
            ]:
                value = obj.get(key)

                if isinstance(value, list):
                    ingredients.extend(value)

            # If two or more ingredients are found,
            # create possible pairs.
            if len(ingredients) >= 2:

                cleaned = [
                    normalize(x)
                    for x in ingredients
                    if normalize(x)
                ]

                for i in range(len(cleaned)):
                    for j in range(i + 1, len(cleaned)):
                        pair = canonical_pair(
                            cleaned[i],
                            cleaned[j]
                        )

                        if pair:
                            source_pairs.add(pair)

            for value in obj.values():
                scan(value)

        elif isinstance(obj, list):

            for value in obj:
                scan(value)

    scan(rules)

    overlap_pairs = source_pairs & existing_pairs
    new_pairs = source_pairs - existing_pairs

    print("\nBSYILMAZ PAIR CHECK")
    print(f"Source pairs       : {len(source_pairs)}")
    print(f"Already existing   : {len(overlap_pairs)}")
    print(f"NEW pairs          : {len(new_pairs)}")

    if new_pairs:
        print("\nNew pairs:")
        for a, b in sorted(new_pairs):
            print(f"  {a} + {b}")

else:
    print("\nBSYILMAZ compatibility rules not found:")
    print(BSYILMAZ_RULES)


# ============================================================
# SCANALYZE
# ============================================================

print("\n" + "-" * 60)
print("SCANALYZE DATASET")
print("-" * 60)

if Path(SCANALYZE).exists():

    scan = pd.read_csv(SCANALYZE)

    print(f"Source rows       : {len(scan)}")

    possible_columns = [
        "Ingredient Name",
        "Ingredient_Name",
        "ingredient_name"
    ]

    ingredient_col = None

    for col in possible_columns:
        if col in scan.columns:
            ingredient_col = col
            break

    if ingredient_col:

        source_ingredients = {
            normalize(x)
            for x in scan[ingredient_col]
            if normalize(x)
        }

        overlap = source_ingredients & existing_ingredients
        new = source_ingredients - existing_ingredients

        print(f"Unique ingredients: {len(source_ingredients)}")
        print(f"Already existing  : {len(overlap)}")
        print(f"New ingredients   : {len(new)}")

        if source_ingredients:
            print(
                f"Overlap percentage: "
                f"{len(overlap) / len(source_ingredients) * 100:.2f}%"
            )

        print("\nNew ingredients:")
        for x in sorted(new):
            print("  ", x)

    else:
        print("Ingredient column not found.")

else:
    print("SCANALYZE file not found:")
    print(SCANALYZE)


# ============================================================
# CURESKIN
# ============================================================

print("\n" + "-" * 60)
print("CURESKIN DATASET")
print("-" * 60)

if Path(CURESKIN).exists():

    cure = pd.read_csv(CURESKIN)

    print(f"Source rows: {len(cure)}")

    possible_columns = [
        "inci_name",
        "INCI Name",
        "ingredient_name",
        "Ingredient Name"
    ]

    ingredient_col = None

    for col in possible_columns:
        if col in cure.columns:
            ingredient_col = col
            break

    if ingredient_col:

        source_ingredients = {
            normalize(x)
            for x in cure[ingredient_col]
            if normalize(x)
        }

        overlap = source_ingredients & existing_ingredients
        new = source_ingredients - existing_ingredients

        print(f"Unique ingredients: {len(source_ingredients)}")
        print(f"Already existing  : {len(overlap)}")
        print(f"New ingredients   : {len(new)}")

        if source_ingredients:
            print(
                f"Overlap percentage: "
                f"{len(overlap) / len(source_ingredients) * 100:.2f}%"
            )

        print("\nNew ingredients:")
        for x in sorted(new):
            print("  ", x)

    else:
        print("Ingredient column not found.")

else:
    print("CURESKIN file not found:")
    print(CURESKIN)


# ============================================================
# END
# ============================================================

print("\n" + "=" * 60)
print("OVERLAP CHECK COMPLETED")
print("=" * 60)
print("NO DATASET WAS MODIFIED.")