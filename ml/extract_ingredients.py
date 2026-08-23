import pandas as pd

INPUT_FILE = "data/clean_dataset.csv"

df = pd.read_csv(INPUT_FILE)

# Get unique ingredients from both columns
ingredients_1 = df["Ingredient_1"].dropna().str.strip()
ingredients_2 = df["Ingredient_2"].dropna().str.strip()

unique_ingredients = sorted(
    set(ingredients_1) | set(ingredients_2)
)

print("\n========== UNIQUE INGREDIENTS ==========\n")

print("Total unique ingredients:", len(unique_ingredients))

for number, ingredient in enumerate(unique_ingredients, start=1):
    print(f"{number}. {ingredient}")

print("\n========================================")
