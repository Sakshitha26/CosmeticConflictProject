from risk.risk_analyzer import analyze_risk


def test_no_conflicts():

    ingredients = [
        "A",
        "B",
        "C"
    ]

    conflicts = []

    result = analyze_risk(
        ingredients,
        conflicts
    )

    assert result["conflict_count"] == 0
    assert result["cumulative_risk"] == 0
    assert result["risk_level"] == "Safe"

    print("Test 1 passed")


def test_low_conflict():

    ingredients = [
        "A",
        "B"
    ]

    conflicts = [
        {
            "ingredient1": "A",
            "ingredient2": "B",
            "severity": "low"
        }
    ]

    result = analyze_risk(
        ingredients,
        conflicts
    )

    assert result["conflict_count"] == 1
    assert result["cumulative_risk"] == 1

    print("Test 2 passed")


def test_medium_conflict():

    ingredients = [
        "A",
        "B"
    ]

    conflicts = [
        {
            "ingredient1": "A",
            "ingredient2": "B",
            "severity": "medium"
        }
    ]

    result = analyze_risk(
        ingredients,
        conflicts
    )

    assert result["cumulative_risk"] == 2

    print("Test 3 passed")


def test_high_conflict():

    ingredients = [
        "A",
        "B"
    ]

    conflicts = [
        {
            "ingredient1": "A",
            "ingredient2": "B",
            "severity": "high"
        }
    ]

    result = analyze_risk(
        ingredients,
        conflicts
    )

    assert result["cumulative_risk"] == 3
    assert result["risk_level"] == "High"

    print("Test 4 passed")


def test_multiple_conflicts():

    ingredients = [
        "A",
        "B",
        "C",
        "D"
    ]

    conflicts = [
        {
            "ingredient1": "A",
            "ingredient2": "B",
            "severity": "high"
        },
        {
            "ingredient1": "A",
            "ingredient2": "C",
            "severity": "medium"
        },
        {
            "ingredient1": "B",
            "ingredient2": "D",
            "severity": "low"
        }
    ]

    result = analyze_risk(
        ingredients,
        conflicts
    )

    assert result["conflict_count"] == 3
    assert result["cumulative_risk"] == 6

    print("Test 5 passed")


def test_all_high():

    ingredients = [
        "A",
        "B",
        "C",
        "D"
    ]

    conflicts = [
        {
            "ingredient1": "A",
            "ingredient2": "B",
            "severity": "high"
        },
        {
            "ingredient1": "A",
            "ingredient2": "C",
            "severity": "high"
        },
        {
            "ingredient1": "A",
            "ingredient2": "D",
            "severity": "high"
        }
    ]

    result = analyze_risk(
        ingredients,
        conflicts
    )

    assert result["conflict_count"] == 3
    assert result["cumulative_risk"] == 9
    assert result["risk_level"] == "High"

    print("Test 6 passed")


if __name__ == "__main__":

    test_no_conflicts()
    test_low_conflict()
    test_medium_conflict()
    test_high_conflict()
    test_multiple_conflicts()
    test_all_high()

    print("\nALL TESTS PASSED!")