import os
import pandas as pd


# ============================================================
# PATH
# ============================================================

EXTERNAL_FILE = (
    "data/external/open_beauty_facts/"
    "external_ingredient_pairs.csv"
)


# ============================================================
# LOAD EXTERNAL EVIDENCE
# ============================================================

def load_external_evidence():

    print("\n========================================")
    print("LOADING EXTERNAL EVIDENCE")
    print("========================================")

    if not os.path.exists(EXTERNAL_FILE):

        print(
            "External evidence file not found:"
        )

        print(EXTERNAL_FILE)

        return {}

    df = pd.read_csv(
        EXTERNAL_FILE
    )

    required = [
        "Ingredient_1",
        "Ingredient_2",
        "Co_Occurrence_Count"
    ]

    missing = [
        col
        for col in required
        if col not in df.columns
    ]

    if missing:

        raise ValueError(
            f"Missing columns in external evidence: {missing}"
        )

    # --------------------------------------------------------
    # CLEAN INGREDIENT NAMES
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # CLEAN CO-OCCURRENCE
    # --------------------------------------------------------

    df["Co_Occurrence_Count"] = pd.to_numeric(
        df["Co_Occurrence_Count"],
        errors="coerce"
    ).fillna(0)

    # --------------------------------------------------------
    # CREATE NORMALIZED PAIR KEY
    # --------------------------------------------------------

    df["Pair_Key"] = (
        df.apply(
            lambda row:
            "||".join(
                sorted([
                    row["Ingredient_1"],
                    row["Ingredient_2"]
                ])
            ),
            axis=1
        )
    )

    # --------------------------------------------------------
    # KEEP MAXIMUM OCCURRENCE FOR DUPLICATES
    # --------------------------------------------------------

    df = (
        df.groupby(
            "Pair_Key",
            as_index=False
        )["Co_Occurrence_Count"]
        .max()
    )

    print(
        "External evidence pairs:",
        len(df)
    )

    # --------------------------------------------------------
    # CONVERT TO DICTIONARY
    # --------------------------------------------------------

    evidence_dict = dict(
        zip(
            df["Pair_Key"],
            df["Co_Occurrence_Count"]
        )
    )

    print(
        "External evidence dictionary created!"
    )

    print(
        "Dictionary entries:",
        len(evidence_dict)
    )

    print(
        "External evidence loaded successfully!"
    )

    return evidence_dict


# ============================================================
# GET EXTERNAL CO-OCCURRENCE
# ============================================================

def get_external_co_occurrence(
    ingredient_1,
    ingredient_2,
    evidence_dict
):

    ingredient_1 = (
        str(ingredient_1)
        .lower()
        .strip()
    )

    ingredient_2 = (
        str(ingredient_2)
        .lower()
        .strip()
    )

    pair_key = "||".join(
        sorted([
            ingredient_1,
            ingredient_2
        ])
    )

    return float(
        evidence_dict.get(
            pair_key,
            0.0
        )
    )