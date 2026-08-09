import json
import os
from itertools import combinations

from engine.ingredient_parser import normalize_ingredient


class ConflictEngine:

    def __init__(self):

        # Project root directory
        base_path = os.path.dirname(os.path.dirname(__file__))

        # Large conflict dataset
        file_path = os.path.join(
            base_path,
            "data",
            "dataset_conflicts.json"
        )

        # Load dataset
        with open(file_path, "r", encoding="utf-8") as file:
            self.conflicts = json.load(file)

        print("=" * 50)
        print("CONFLICT DATASET LOADED")
        print("Dataset:", file_path)
        print("TOTAL RULES LOADED:", len(self.conflicts))
        print("=" * 50)

    def check_conflicts(self, ingredients):

        found_conflicts = []

        # Normalize ingredients
        ingredients = [
            normalize_ingredient(ingredient)
            for ingredient in ingredients
            if ingredient
        ]

        # Remove duplicates
        ingredients = list(set(ingredients))

        # Create ingredient pairs
        ingredient_pairs = combinations(ingredients, 2)

        # Compare pairs with dataset
        for ingredient_a, ingredient_b in ingredient_pairs:

            for conflict in self.conflicts:

                rule_a = normalize_ingredient(
                    conflict["ingredient_1"]
                )

                rule_b = normalize_ingredient(
                    conflict["ingredient_2"]
                )

                # Check both orders
                if (
                    (ingredient_a == rule_a and ingredient_b == rule_b)
                    or
                    (ingredient_a == rule_b and ingredient_b == rule_a)
                ):
                    found_conflicts.append(conflict)

        return found_conflicts

    def compare_products(self, product1, product2):

        conflicts = []

        # Normalize Product 1
        product1 = [
            normalize_ingredient(ingredient)
            for ingredient in product1
            if ingredient
        ]

        # Normalize Product 2
        product2 = [
            normalize_ingredient(ingredient)
            for ingredient in product2
            if ingredient
        ]

        # Compare every ingredient from Product 1
        # with every ingredient from Product 2
        for ingredient_a in product1:

            for ingredient_b in product2:

                for conflict in self.conflicts:

                    rule_a = normalize_ingredient(
                        conflict["ingredient_1"]
                    )

                    rule_b = normalize_ingredient(
                        conflict["ingredient_2"]
                    )

                    # Check both orders
                    if (
                        (ingredient_a == rule_a and ingredient_b == rule_b)
                        or
                        (ingredient_a == rule_b and ingredient_b == rule_a)
                    ):

                        conflicts.append(conflict)

        return conflicts

    def calculate_overall_severity(self, conflicts):

        if not conflicts:
            return "safe"

        severities = [
            str(conflict["severity"]).lower()
            for conflict in conflicts
        ]

        if "high" in severities:
            return "high"

        if "medium" in severities:
            return "medium"

        if "low" in severities:
            return "low"

        return "safe"

    def get_status(self, conflicts_or_severity):

        if isinstance(conflicts_or_severity, list):

            severity = self.calculate_overall_severity(
                conflicts_or_severity
            )

        else:

            severity = str(
                conflicts_or_severity
            ).lower()

        if severity == "high":
            return "WARNING"

        if severity == "medium":
            return "CAUTION"

        if severity == "low":
            return "CAUTION"

        return "SAFE"