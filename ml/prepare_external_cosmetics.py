import pandas as pd
import os

# ==========================================
# PATHS
# ==========================================

INPUT_FILE = "data/external/open_beauty_facts/open_beauty_facts_raw.csv"

OUTPUT_FILE = "data/external/open_beauty_facts/open_beauty_facts_clean.csv"


# ==========================================
# LOAD DATA
# ==========================================

print("Loading Open Beauty Facts dataset...")

df = pd.read_csv(
    INPUT_FILE,
    sep="\t",
    low_memory=False
)

print("Original rows:", len(df))


# ==========================================
# FIND INGREDIENT COLUMN
# ==========================================

ingredient_column = None

possible_columns = [
    "ingredients_text",
    "ingredientsText",
    "ingredients"
]

for column in possible_columns:
    if column in df.columns:
        ingredient_column = column
        break

if ingredient_column is None:
    raise ValueError("Ingredient column was not found.")

print("Using ingredient column:", ingredient_column)


# ==========================================
# KEEP USEFUL COLUMNS
# ==========================================

wanted_columns = []

for column in [
    "code",
    "product_name",
    "brands",
    "categories",
    "countries",
    ingredient_column
]:
    if column in df.columns:
        wanted_columns.append(column)

df = df[wanted_columns].copy()


# ==========================================
# REMOVE EMPTY INGREDIENT LISTS
# ==========================================

df[ingredient_column] = (
    df[ingredient_column]
    .fillna("")
    .astype(str)
    .str.strip()
)

df = df[df[ingredient_column] != ""]

df = df[df[ingredient_column].str.lower() != "nan"]


# ==========================================
# REMOVE DUPLICATE PRODUCTS
# ==========================================

if "code" in df.columns:
    df = df.drop_duplicates(subset=["code"])
else:
    df = df.drop_duplicates()


# ==========================================
# RESET INDEX
# ==========================================

df = df.reset_index(drop=True)


# ==========================================
# SAVE
# ==========================================

os.makedirs(
    os.path.dirname(OUTPUT_FILE),
    exist_ok=True
)

df.to_csv(
    OUTPUT_FILE,
    index=False
)


# ==========================================
# SUMMARY
# ==========================================

print("\n==========================================")
print("OPEN BEAUTY FACTS CLEANING COMPLETED")
print("==========================================")

print("Products retained:", len(df))

print("Output:", OUTPUT_FILE)

print("\nSample data:")

print(
    df.head(5).to_string(index=False)
)

print("\n==========================================")