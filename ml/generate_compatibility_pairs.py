import json
import pandas as pd
from itertools import product


RULES_FILE = "data/compatibility_source/compatibility_rules.json"
OUTPUT_FILE = "data/external_compatibility_pairs.csv"


def normalize_name(name):
    """
    Convert source ingredient names into a consistent format.
    Example:
        ascorbic-acid -> ascorbic acid
        benzoyl-peroxide -> benzoyl peroxide
    """
    return name.strip().lower().replace("-", " ")


def main():

    print("=" * 60)
    print("GENERATING COMPATIBILITY INGREDIENT PAIRS")
    print("=" * 60)

    # ---------------------------------------------------------
    # 1. Load compatibility rules
    # ---------------------------------------------------------

    print("\nLoading compatibility rules...")

    with open(RULES_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    groups = data["groups"]
    rules = data["rules"]

    print("Ingredient groups:", len(groups))
    print("Compatibility rules:", len(rules))

    # ---------------------------------------------------------
    # 2. Generate individual ingredient pairs
    # ---------------------------------------------------------

    generated_rows = []

    for rule in rules:

        group_a = rule["a"]
        group_b = rule["b"]

        severity = rule["severity"]
        reason = rule.get("reason", "")
        recommendation = rule.get("recommendation", "")

        ingredients_a = groups.get(group_a, [])
        ingredients_b = groups.get(group_b, [])

        if not ingredients_a or not ingredients_b:
            continue

        for ingredient_a, ingredient_b in product(
            ingredients_a,
            ingredients_b
        ):

            ing1 = normalize_name(ingredient_a)
            ing2 = normalize_name(ingredient_b)

            # Prevent same ingredient pair
            if ing1 == ing2:
                continue

            # -------------------------------------------------
            # Convert source severity to project severity
            # -------------------------------------------------

            if severity == "avoid":
                project_severity = "High Risk"

            elif severity == "caution":
                project_severity = "Medium Risk"

            elif severity in ["great", "good", "essential"]:
                project_severity = "Safe"

            else:
                project_severity = "Safe"

            note = (
                f"Source compatibility rule: {severity}. "
                f"{reason} "
                f"Recommendation: {recommendation}"
            )

            generated_rows.append({
                "Ingredient_1": ing1,
                "Ingredient_2": ing2,
                "Severity": project_severity,
                "Severity_Note": note
            })

    # ---------------------------------------------------------
    # 3. Convert to DataFrame
    # ---------------------------------------------------------

    df = pd.DataFrame(generated_rows)

    if df.empty:
        print("\nERROR: No pairs were generated.")
        return

    # ---------------------------------------------------------
    # 4. Remove duplicate pairs
    # ---------------------------------------------------------

    def pair_key(row):
        return tuple(sorted([
            row["Ingredient_1"],
            row["Ingredient_2"]
        ]))

    df["_pair_key"] = df.apply(pair_key, axis=1)

    # Keep the first occurrence
    df = df.drop_duplicates(
        subset=["_pair_key"],
        keep="first"
    )

    df = df.drop(columns=["_pair_key"])

    # ---------------------------------------------------------
    # 5. Sort
    # ---------------------------------------------------------

    severity_order = {
        "High Risk": 0,
        "Medium Risk": 1,
        "Safe": 2
    }

    df["_order"] = df["Severity"].map(severity_order)

    df = df.sort_values(
        by=["_order", "Ingredient_1", "Ingredient_2"]
    )

    df = df.drop(columns=["_order"])

    # ---------------------------------------------------------
    # 6. Save
    # ---------------------------------------------------------

    df.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8"
    )

    # ---------------------------------------------------------
    # 7. Display results
    # ---------------------------------------------------------

    print("\nCompatibility pairs generated successfully!")

    print("\nOutput file:")
    print(OUTPUT_FILE)

    print("\nTotal generated pairs:", len(df))

    print("\nSeverity distribution:")
    print(df["Severity"].value_counts())

    print("\nHigh-risk pairs:")
    high = df[df["Severity"] == "High Risk"]

    if high.empty:
        print("No High Risk pairs found.")
    else:
        print(
            high[
                [
                    "Ingredient_1",
                    "Ingredient_2",
                    "Severity"
                ]
            ].to_string(index=False)
        )

    print("\nMedium-risk pairs:")
    medium = df[df["Severity"] == "Medium Risk"]

    print(
        medium[
            [
                "Ingredient_1",
                "Ingredient_2",
                "Severity"
            ]
        ].to_string(index=False)
    )

    print("\nDone!")


if __name__ == "__main__":
    main()