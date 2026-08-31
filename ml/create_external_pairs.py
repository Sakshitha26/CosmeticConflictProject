import pandas as pd
from itertools import combinations

INPUT_FILE = (
    "data/external/open_beauty_facts/"
    "external_ingredient_occurrences.csv"
)

OUTPUT_FILE = (
    "data/external/open_beauty_facts/"
    "external_ingredient_pairs.csv"
)

print("Loading ingredient occurrences...")

df = pd.read_csv(INPUT_FILE)

print("Ingredient records:", len(df))

pairs = {}

for product_code, group in df.groupby("product_code"):

    ingredients = sorted(
        set(
            group["ingredient"]
            .dropna()
            .astype(str)
        )
    )

    if len(ingredients) > 100:
        ingredients = ingredients[:100]

    for ingredient1, ingredient2 in combinations(
        ingredients, 2
    ):

        key = (
            ingredient1,
            ingredient2
        )

        pairs[key] = pairs.get(key, 0) + 1


records = []

for (
    ingredient1,
    ingredient2
), count in pairs.items():

    records.append({
        "Ingredient_1": ingredient1,
        "Ingredient_2": ingredient2,
        "Co_Occurrence_Count": count
    })


result = pd.DataFrame(records)

result = result.sort_values(
    "Co_Occurrence_Count",
    ascending=False
)

result.to_csv(
    OUTPUT_FILE,
    index=False
)

print("\n==========================================")
print("EXTERNAL PAIR GENERATION COMPLETE")
print("==========================================")

print(
    "Unique ingredient pairs:",
    len(result)
)

print("Output:", OUTPUT_FILE)

print("\nTop pairs:")

print(
    result.head(20).to_string(index=False)
)
