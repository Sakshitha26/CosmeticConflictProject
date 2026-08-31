import pandas as pd
import re

INPUT_FILE = (
    "data/external/open_beauty_facts/"
    "open_beauty_facts_clean.csv"
)

OUTPUT_FILE = (
    "data/external/open_beauty_facts/"
    "external_ingredient_occurrences.csv"
)

print("Loading cleaned dataset...")

df = pd.read_csv(
    INPUT_FILE,
    low_memory=False
)

print("Products:", len(df))

possible_columns = [
    "ingredients_text",
    "ingredientsText",
    "ingredients"
]

ingredient_column = None

for column in possible_columns:
    if column in df.columns:
        ingredient_column = column
        break

if ingredient_column is None:
    raise ValueError("Ingredient column not found.")

print("Using ingredient column:", ingredient_column)

records = []

for _, row in df.iterrows():

    text = str(row[ingredient_column])

    if not text or text.lower() == "nan":
        continue

    ingredients = re.split(r",|;", text)

    cleaned = []

    for ingredient in ingredients:

        ingredient = ingredient.strip().lower()

        ingredient = re.sub(
            r"\([^)]*\)",
            "",
            ingredient
        )

        ingredient = re.sub(
            r"\s+",
            " ",
            ingredient
        )

        ingredient = ingredient.strip()

        if len(ingredient) < 2:
            continue

        cleaned.append(ingredient)

    cleaned = list(dict.fromkeys(cleaned))

    for ingredient in cleaned:

        records.append({
            "product_code": row.get("code", ""),
            "product_name": row.get("product_name", ""),
            "ingredient": ingredient
        })

result = pd.DataFrame(records)

result = result.drop_duplicates()

result.to_csv(
    OUTPUT_FILE,
    index=False
)

print("\n==========================================")
print("EXTERNAL INGREDIENT EXTRACTION COMPLETE")
print("==========================================")

print("Ingredient records:", len(result))

print(
    "Unique ingredients:",
    result["ingredient"].nunique()
)

print("Output:", OUTPUT_FILE)

print("\nSample:")
print(
    result.head(10).to_string(index=False)
)