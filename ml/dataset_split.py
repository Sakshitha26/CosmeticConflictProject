import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split

# Project directory
BASE_DIR = Path(__file__).resolve().parent.parent

input_path = BASE_DIR / "data" / "ml_ready_dataset.csv"
data_dir = BASE_DIR / "data"

# Load dataset
df = pd.read_csv(input_path)

print("DATASET SPLITTING")
print("Total rows:", len(df))

# Remove rows with missing target
df = df.dropna(subset=["target"])

# First split: 80% train, 20% temporary
train, temp = train_test_split(
    df,
    test_size=0.20,
    random_state=42,
    stratify=df["target"]
)

# Split remaining 20% into:
# 10% validation
# 10% test
validation, test = train_test_split(
    temp,
    test_size=0.50,
    random_state=42
)

# Save files
train_path = data_dir / "train.csv"
validation_path = data_dir / "validation.csv"
test_path = data_dir / "test.csv"

train.to_csv(train_path, index=False)
validation.to_csv(validation_path, index=False)
test.to_csv(test_path, index=False)

print()
print("SPLIT COMPLETE")
print("Training rows:", len(train))
print("Validation rows:", len(validation))
print("Testing rows:", len(test))

print()
print("TRAIN DISTRIBUTION")
print(train["target"].value_counts())

print()
print("VALIDATION DISTRIBUTION")
print(validation["target"].value_counts())

print()
print("TEST DISTRIBUTION")
print(test["target"].value_counts())

print()
print("Saved:")
print(train_path)
print(validation_path)
print(test_path)
