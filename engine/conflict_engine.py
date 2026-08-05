import json
import os
from itertools import combinations

from engine.ingredient_parser import normalize_ingredient


class ConflictEngine:

    def __init__(self):
        base_path = os.path.dirname(os.path.dirname(__file__))
        file_path = os.path.join(base_path, "data", "conflicts.json")

        with open(file_path, "r", encoding="utf-8") as file:
            self.conflicts = json.load(file)

    def check_conflicts(self, ingredients):

        found_conflicts = []

        # Normalize all ingredients
        ingredients = [
            normalize_ingredient(ingredient)
            for ingredient in ingredients
        ]

        # Remove duplicate ingredients
        ingredients = list(set(ingredients))

        # Create every possible ingredient pair
        ingredient_pairs = combinations(ingredients, 2)

        # Check each pair against the conflict database
        for ingredient_a, ingredient_b in ingredient_pairs:

            for conflict in self.conflicts:

                rule_a = normalize_ingredient(conflict["ingredient_1"])
                rule_b = normalize_ingredient(conflict["ingredient_2"])

                # Check both possible orders
                if (
                    (ingredient_a == rule_a and ingredient_b == rule_b)
                    or
                    (ingredient_a == rule_b and ingredient_b == rule_a)
                ):
                    found_conflicts.append(conflict)

        return found_conflicts

    def calculate_overall_severity(self, conflicts):

        if not conflicts:
            return "none"

        severities = [
            conflict["severity"].lower()
            for conflict in conflicts
        ]

        if "high" in severities:
            return "high"

        if "medium" in severities:
            return "medium"

        return "low"

    def analyze(self, ingredients):

        conflicts = self.check_conflicts(ingredients)

        overall_severity = self.calculate_overall_severity(conflicts)

        if overall_severity == "high":
            status = "WARNING"

        elif overall_severity == "medium":
            status = "CAUTION"

        elif overall_severity == "low":
            status = "LOW RISK"

        else:
            status = "SAFE"

        return {
            "ingredients": ingredients,
            "conflict_count": len(conflicts),
            "conflicts": conflicts,
            "overall_severity": overall_severity,
            "status": status
        }