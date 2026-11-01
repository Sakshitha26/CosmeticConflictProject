
from risk.cci import (
    calculate_cumulative_risk,
    calculate_conflict_density,
    calculate_cci,
    classify_risk
)


def get_recommendation(risk_level):
    """
    Generate recommendation based on risk level.
    """

    recommendations = {
        "Safe": "No major conflicts detected.",
        "Low": "Use with caution.",
        "Medium": "Consider avoiding simultaneous use.",
        "High": "Avoid combining these products."
    }

    return recommendations.get(
        risk_level,
        "No recommendation available."
    )


def analyze_risk(ingredients, conflicts):
    """
    Perform complete cosmetic risk analysis.
    """

    conflict_count = len(conflicts)

    cumulative_risk = calculate_cumulative_risk(
        conflicts
    )

    conflict_density = calculate_conflict_density(
        ingredients,
        conflicts
    )

    cci_score = calculate_cci(
        ingredients,
        conflicts
    )

    risk_level = classify_risk(
        cci_score
    )

    recommendation = get_recommendation(
        risk_level
    )

    return {
        "cci_score": cci_score,
        "risk_level": risk_level,
        "conflict_count": conflict_count,
        "cumulative_risk": cumulative_risk,
        "conflict_density": conflict_density,
        "recommendation": recommendation
    }


def analyze_what_if(
    ingredients,
    conflicts,
    selected_ingredient_1,
    selected_ingredient_2
):
    """
    Simulate excluding one ingredient conflict pair
    and recalculate the cosmetic risk analysis.

    Original conflicts and ingredients remain unchanged.
    """

    from engine.ingredient_parser import normalize_ingredient

    # Validate selected ingredients
    if not selected_ingredient_1 or not selected_ingredient_2:
        raise ValueError(
            "Both selected ingredients are required."
        )

    ingredient_1 = normalize_ingredient(
        selected_ingredient_1
    )

    ingredient_2 = normalize_ingredient(
        selected_ingredient_2
    )

    if not ingredient_1 or not ingredient_2:
        raise ValueError(
            "Invalid ingredient pair selected."
        )

    if ingredient_1 == ingredient_2:
        raise ValueError(
            "Both ingredients must be different."
        )

    # Store selected pair without considering order
    selected_pair = frozenset([
        ingredient_1,
        ingredient_2
    ])

    # Create a separate list without the selected conflict
    remaining_conflicts = []
    pair_found = False

    for conflict in conflicts:

        conflict_ingredient_1 = normalize_ingredient(
            conflict.get("ingredient_1", "")
        )

        conflict_ingredient_2 = normalize_ingredient(
            conflict.get("ingredient_2", "")
        )

        conflict_pair = frozenset([
            conflict_ingredient_1,
            conflict_ingredient_2
        ])

        # Exclude only the selected pair
        if conflict_pair == selected_pair:
            pair_found = True
        else:
            remaining_conflicts.append(conflict)

    # Check whether selected pair exists
    if not pair_found:
        raise ValueError(
            "Selected ingredient pair was not found in conflicts."
        )

    # Calculate original risk
    original_result = analyze_risk(
        ingredients,
        conflicts
    )

    # Recalculate risk after excluding selected pair
    updated_result = analyze_risk(
        ingredients,
        remaining_conflicts
    )

    # Return original and simulated results
    return {
        "excluded_pair": {
            "ingredient_1": selected_ingredient_1,
            "ingredient_2": selected_ingredient_2
        },

        "original_cci": original_result["cci_score"],
        "original_risk": original_result["risk_level"],

        "updated_cci": updated_result["cci_score"],
        "updated_risk": updated_result["risk_level"],

        "original_conflict_count": len(conflicts),
        "remaining_conflict_count": len(remaining_conflicts),

        "remaining_conflicts": remaining_conflicts,

        "original_analysis": original_result,
        "updated_analysis": updated_result
    }
