import pandas as pd
from sklearn.utils import resample

INPUT_FILE = "data/ingredient_pairs_augmented.xlsx"
OUTPUT_FILE = "data/ingredient_pairs_balanced.xlsx"

print("=" * 60)
print("BALANCING COSMETIC SEVERITY DATASET")
print("=" * 60)

# Load dataset
df = pd.read_excel(INPUT_FILE)

print("\nOriginal distribution:")
print(df["Severity"].value_counts())

# Separate classes
safe = df[df["Severity"] == "Safe"]
medium = df[df["Severity"] == "Medium Risk"]
high = df[df["Severity"] == "High Risk"]

# Target sizes
# Safe is kept smaller to reduce dominance.
# Medium and High are oversampled.
medium_target = 500
high_target = 300

medium_balanced = resample(
    medium,
    replace=True,
    n_samples=medium_target,
    random_state=42
)

high_balanced = resample(
    high,
    replace=True,
    n_samples=high_target,
    random_state=42
)

# Keep all Safe examples
balanced_df = pd.concat(
    [safe, medium_balanced, high_balanced],
    ignore_index=True
)

# Shuffle
balanced_df = balanced_df.sample(
    frac=1,
    random_state=42
).reset_index(drop=True)

# Save
balanced_df.to_excel(OUTPUT_FILE, index=False)

print("\nBalanced distribution:")
print(balanced_df["Severity"].value_counts())

print("\nPercentages:")
print(
    balanced_df["Severity"]
    .value_counts(normalize=True)
    .mul(100)
    .round(2)
)

print("\nOutput:")
print(OUTPUT_FILE)

print("=" * 60)