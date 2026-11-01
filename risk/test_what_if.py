
from risk.risk_analyzer import analyze_what_if


# Sample ingredients
ingredients = [
    "Limonene",
    "Lactic Acid",
    "Fragrance"
]

# Sample conflicts
conflicts = [
    {
        "ingredient_1": "Limonene",
        "ingredient_2": "Lactic Acid",
        "severity": "high"
    },
    {
        "ingredient_1": "Fragrance",
        "ingredient_2": "Limonene",
        "severity": "medium"
    }
]


def test_what_if_excludes_selected_pair():

    result = analyze_what_if(
        ingredients,
        conflicts,
        "Limonene",
        "Lactic Acid"
    )

    assert result["original_conflict_count"] == 2
    assert result["remaining_conflict_count"] == 1

    remaining = result["remaining_conflicts"]

    assert remaining[0]["ingredient_1"] == "Fragrance"
    assert remaining[0]["ingredient_2"] == "Limonene"

    print("Test 1 passed: Selected pair excluded")


def test_reverse_order():

    result = analyze_what_if(
        ingredients,
        conflicts,
        "Lactic Acid",
        "Limonene"
    )

    assert result["remaining_conflict_count"] == 1

    print("Test 2 passed: Reverse order handled")


def test_original_conflicts_unchanged():

    original_count = len(conflicts)

    analyze_what_if(
        ingredients,
        conflicts,
        "Limonene",
        "Lactic Acid"
    )

    assert len(conflicts) == original_count

    print("Test 3 passed: Original conflicts unchanged")


def test_invalid_pair():

    try:
        analyze_what_if(
            ingredients,
            conflicts,
            "Water",
            "Vitamin C"
        )

        assert False, "Expected ValueError"

    except ValueError:
        print("Test 4 passed: Invalid pair handled")


def test_no_conflicts_remain():

    result = analyze_what_if(
        ["Limonene", "Lactic Acid"],
        [
            {
                "ingredient_1": "Limonene",
                "ingredient_2": "Lactic Acid",
                "severity": "high"
            }
        ],
        "Limonene",
        "Lactic Acid"
    )

    assert result["remaining_conflict_count"] == 0
    assert result["updated_cci"] == 0.0
    assert result["updated_risk"] == "Safe"

    print("Test 5 passed: No conflicts remaining")


if __name__ == "__main__":

    test_what_if_excludes_selected_pair()
    test_reverse_order()
    test_original_conflicts_unchanged()
    test_invalid_pair()
    test_no_conflicts_remain()

    print("\nALL WHAT-IF TESTS PASSED!")
