import pandas as pd

# Load normalized dataset
df = pd.read_csv("data/normalized_dataset.csv")

# Get all unique ingredients
ingredients = sorted(
    set(df["Ingredient_1"].dropna()) |
    set(df["Ingredient_2"].dropna())
)

# Create ingredient properties table
properties = pd.DataFrame({
    "ingredient": ingredients,
    "exfoliant": 0,
    "retinoid": 0,
    "antioxidant": 0,
    "drying_agent": 0,
    "humectant": 0,
    "emollient": 0,
    "preservative": 0,
    "fragrance": 0,
    "active_ingredient": 0
})

# Known functional categories
exfoliants = {
    "Citric Acid",
    "Glycolic Acid",
    "Lactic Acid"
}

antioxidants = {
    "Bht",
    "Tocopherol",
    "Tocopheryl Acetate",
    "Green Tea Extract"
}

humectants = {
    "Glycerin",
    "Sodium Hyaluronate",
    "Panthenol",
    "Sorbitol",
    "Butylene Glycol",
    "Pentylene Glycol",
    "Propylene Glycol",
    "Propanediol"
}

fragrances = {
    "Fragrance",
    "Geraniol",
    "Limonene",
    "Linalool"
}

preservatives = {
    "Phenoxyethanol",
    "Potassium Sorbate",
    "Sodium Benzoate",
    "Chlorphenesin"
}

# Assign properties
for i, ingredient in enumerate(properties["ingredient"]):

    if ingredient in exfoliants:
        properties.loc[i, "exfoliant"] = 1

    if ingredient in antioxidants:
        properties.loc[i, "antioxidant"] = 1

    if ingredient in humectants:
        properties.loc[i, "humectant"] = 1

    if ingredient in fragrances:
        properties.loc[i, "fragrance"] = 1

    if ingredient in preservatives:
        properties.loc[i, "preservative"] = 1

# Save
properties.to_csv(
    "data/ingredient_properties.csv",
    index=False
)

print("INGREDIENT PROPERTIES CREATED")
print("Total ingredients:", len(properties))
print("Saved to: data/ingredient_properties.csv")
print()
print(properties.to_string(index=False))