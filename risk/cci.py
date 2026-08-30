SEVERITY_WEIGHT = {
    "low": 1,
    "medium": 2,
    "high": 3
}


def calculate_cumulative_risk(conflicts):
    """
    Calculate total severity score of all conflicts.
    """

    total = 0

    for conflict in conflicts:
        severity = conflict.get("severity", "").lower()

        total += SEVERITY_WEIGHT.get(severity, 0)

    return total


def calculate_conflict_density(ingredients, conflicts):
    """
    Conflict Density =
    Number of detected conflicts /
    Number of possible ingredient pairs
    """

    n = len(ingredients)

    if n < 2:
        return 0.0

    possible_pairs = n * (n - 1) / 2

    density = len(conflicts) / possible_pairs

    return round(density, 4)


def calculate_cci(ingredients, conflicts):
    """
    Calculate Cosmetic Conflict Index (CCI).

    CCI combines:
    - Cumulative Risk
    - Conflict Density
    - Severity

    Formula:

    CCI = (Cumulative Risk / Maximum Possible Risk) * 70
          + Conflict Density * 30

    Maximum possible risk =
    Number of possible pairs * 3

    Final CCI is between 0 and 100.
    """

    if len(ingredients) < 2:
        return 0.0

    possible_pairs = len(ingredients) * (len(ingredients) - 1) / 2

    cumulative_risk = calculate_cumulative_risk(conflicts)

    maximum_possible_risk = possible_pairs * 3

    if maximum_possible_risk == 0:
        return 0.0

    severity_score = cumulative_risk / maximum_possible_risk

    density = calculate_conflict_density(
        ingredients,
        conflicts
    )

    cci = (severity_score * 70) + (density * 30)

    return round(min(cci, 100), 2)


def classify_risk(cci):
    """
    Convert CCI score into risk category.
    """

    if cci == 0:
        return "Safe"

    elif cci <= 25:
        return "Low"

    elif cci < 50:
        return "Medium"

    else:
        return "High"