import pandas as pd
import os

INPUT_FILE = "data/ingredient_pairs_3000_severity.xlsx"
OUTPUT_FILE = "data/ingredient_pairs_augmented.xlsx"

# Known high-risk cosmetic ingredient combinations
HIGH_RISK_PAIRS = [
    ("retinol", "benzoyl peroxide"),
    ("retinol", "salicylic acid"),
    ("retinol", "glycolic acid"),
    ("retinol", "lactic acid"),
    ("retinol", "mandelic acid"),
    ("retinol", "azelaic acid"),

    ("benzoyl peroxide", "salicylic acid"),
    ("benzoyl peroxide", "glycolic acid"),
    ("benzoyl peroxide", "lactic acid"),
    ("benzoyl peroxide", "mandelic acid"),

    ("salicylic acid", "glycolic acid"),
    ("salicylic acid", "lactic acid"),
    ("salicylic acid", "mandelic acid"),

    ("ascorbic acid", "benzoyl peroxide"),
    ("vitamin c", "benzoyl peroxide"),

    ("retinol", "vitamin c"),
    ("retinol", "ascorbic acid"),

    ("aha", "retinol"),
    ("bha", "retinol"),

    ("tretinoin", "benzoyl peroxide"),
    ("tretinoin", "salicylic acid"),
]


print("Loading original dataset...")

df = pd.read_excel(INPUT_FILE)

print("Original rows:", len(df))


# Normalize
df["Ingredient_1"] = (
    df["Ingredient_1"]
    .astype(str)
    .str.lower()
    .str.strip()
)

df["Ingredient_2"] = (
    df["Ingredient_2"]
    .astype(str)
    .str.lower()
    .str.strip()
)


# Create normalized pair keys
def pair_key(a, b):
    return "||".join(sorted([a, b]))


existing_pairs = set(
    df.apply(
        lambda row: pair_key(
            row["Ingredient_1"],
            row["Ingredient_2"]
        ),
        axis=1
    )
)


new_rows = []


for ingredient_1, ingredient_2 in HIGH_RISK_PAIRS:

    key = pair_key(
        ingredient_1,
        ingredient_2
    )

    # Don't duplicate an existing pair
    if key in existing_pairs:
        continue

    new_rows.append({

        "Ingredient_1": ingredient_1,

        "Ingredient_2": ingredient_2,

        "Co_Occurrence_Count": 0,

        "Severity": "High Risk",

        "Severity_Note":
            "Known high-risk ingredient combination"
    })


augmentation_df = pd.DataFrame(
    new_rows
)


print(
    "New High Risk rows:",
    len(augmentation_df)
)


# Combine
result = pd.concat(
    [
        df,
        augmentation_df
    ],
    ignore_index=True
)


# Remove duplicates
result = result.drop_duplicates(
    subset=[
        "Ingredient_1",
        "Ingredient_2"
    ]
)


# Save
result.to_excel(
    OUTPUT_FILE,
    index=False
)


print("\n========================================")
print("HIGH RISK AUGMENTATION COMPLETE")
print("========================================")

print(
    "Original rows:",
    len(df)
)

print(
    "Added High Risk rows:",
    len(augmentation_df)
)

print(
    "Final rows:",
    len(result)
)

print("\nFinal severity distribution:")

print(
    result["Severity"].value_counts()
)

print("\nOutput:")
print(OUTPUT_FILE)