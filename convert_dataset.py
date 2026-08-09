import pandas as pd
import json
import os

excel_path = "data/ingredient_pairs_3000_severity.xlsx"
json_path = "data/dataset_conflicts.json"

df = pd.read_excel(
    excel_path,
    sheet_name="Ingredient Pairs",
    engine="openpyxl"
)
rules = []

for _, row in df.iterrows():

    severity = str(row["Severity"]).strip()

    if severity == "High Risk":
        severity_value = "high"
    elif severity == "Medium Risk":
        severity_value = "medium"
    else:
        severity_value = "safe"

    rules.append({
        "ingredient_1": str(row["Ingredient_1"]).strip().lower(),
        "ingredient_2": str(row["Ingredient_2"]).strip().lower(),
        "severity": severity_value,
        "reason": str(row["Severity_Note"]).strip(),
        "co_occurrence_count": int(row["Co_Occurrence_Count"])
    })

with open(json_path, "w", encoding="utf-8") as file:
    json.dump(rules, file, indent=4, ensure_ascii=False)

print("Dataset converted successfully!")
print("Total rules:", len(rules))