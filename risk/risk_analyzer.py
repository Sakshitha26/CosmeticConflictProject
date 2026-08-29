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