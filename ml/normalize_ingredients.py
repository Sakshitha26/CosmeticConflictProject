import pandas as pd

INPUT_FILE = "data/clean_dataset.csv"
OUTPUT_FILE = "data/normalized_dataset.csv"

print("\n========== INGREDIENT NORMALIZATION ==========\n")

# Read cleaned dataset
df = pd.read_csv(INPUT_FILE)

# Clean whitespace
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

# Standardize capitalization
df["Ingredient_1"] = df["Ingredient_1"].str.title()
df["Ingredient_2"] = df["Ingredient_2"].str.title()

# Known duplicate spelling/capitalization
# These two names refer to the same ingredient.
ingredient_aliases = {
    "Disodium Edta": "Disodium EDTA"
}

df["Ingredient_1"] = df["Ingredient_1"].replace(ingredient_aliases)
df["Ingredient_2"] = df["Ingredient_2"].replace(ingredient_aliases)

# Save normalized dataset
df.to_csv(
    OUTPUT_FILE,
    index=False,
    encoding="utf-8"
)

# Find unique ingredients after normalization
unique_ingredients = sorted(
    set(df["Ingredient_1"]) |
    set(df["Ingredient_2"])
)

print("Unique ingredients after normalization:",
      len(unique_ingredients))

print("\nUnique ingredients:\n")

for number, ingredient in enumerate(unique_ingredients, start=1):
    print(f"{number}. {ingredient}")

print("\nNormalized dataset saved to:")
print(OUTPUT_FILE)

print("\n==============================================\n")
