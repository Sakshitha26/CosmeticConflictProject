import pandas as pd
from pathlib import Path

# Dataset path
dataset_path = Path("data/ingredient_pairs_3000_severity.xlsx")

print("\n========== DATASET INSPECTION ==========\n")

# Check if dataset exists
if not dataset_path.exists():
    print("ERROR: Dataset file not found!")
    print("Expected location:", dataset_path)
    exit()

# Read Excel dataset
df = pd.read_excel(dataset_path)

# Number of rows and columns
print("Number of rows:", len(df))
print("Number of columns:", len(df.columns))

# Column names
print("\n========== COLUMN NAMES ==========\n")

for column in df.columns:
    print("-", column)

# First 5 rows
print("\n========== FIRST 5 ROWS ==========\n")
print(df.head().to_string())

# Data types
print("\n========== DATA TYPES ==========\n")
print(df.dtypes)

# Missing values
print("\n========== MISSING VALUES ==========\n")
print(df.isnull().sum())

# Duplicate rows
print("\n========== DUPLICATE ROWS ==========\n")
print("Number of duplicate rows:", df.duplicated().sum())

# Unique values
print("\n========== UNIQUE VALUES ==========\n")

for column in df.columns:
    print(f"\n{column}:")
    print(df[column].unique()[:20])

# Find severity column
severity_columns = [
    column for column in df.columns
    if "severity" in column.lower()
]

if severity_columns:
    severity_column = severity_columns[0]

    print("\n========== SEVERITY DISTRIBUTION ==========\n")
    print("Severity column:", severity_column)
    print(df[severity_column].value_counts(dropna=False))

else:
    print("\nNo column containing 'severity' was found.")

print("\n========== INSPECTION COMPLETE ==========\n")