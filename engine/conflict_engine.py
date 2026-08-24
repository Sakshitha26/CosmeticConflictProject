import json
import os
from itertools import combinations

from engine.ingredient_parser import normalize_ingredient


class ConflictEngine:

    def __init__(self):

        # ==========================================
        # PROJECT ROOT DIRECTORY
        # ==========================================

        base_path = os.path.dirname(
            os.path.dirname(__file__)
        )

        # ==========================================
        # CONFLICT DATASET
        # ==========================================

        file_path = os.path.join(
            base_path,
            "data",
            "dataset_conflicts.json"
        )

        # Load dataset
        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as file:

            self.conflicts = json.load(file)

        print("=" * 50)
        print("CONFLICT DATASET LOADED")
        print("Dataset:", file_path)
        print(
            "TOTAL RULES LOADED:",
            len(self.conflicts)
        )
        print("=" * 50)

    # ==========================================
    # CHECK CONFLICTS WITHIN ONE INGREDIENT LIST
    # ==========================================

    def check_conflicts(self, ingredients):

        found_conflicts = []

        # Normalize ingredients
        ingredients = [
            normalize_ingredient(ingredient)
            for ingredient in ingredients
            if ingredient
        ]

        # Remove empty values and duplicates
        ingredients = list(
            set(
                ingredient
                for ingredient in ingredients
                if ingredient
            )
        )

        # Create every possible pair
        ingredient_pairs = combinations(
            ingredients,
            2
        )

        # Track already-found pairs
        seen = set()

        # Compare every pair with dataset
        for ingredient_a, ingredient_b in ingredient_pairs:

            for conflict in self.conflicts:

                rule_a = normalize_ingredient(
                    conflict.get("ingredient_1", "")
                )

                rule_b = normalize_ingredient(
                    conflict.get("ingredient_2", "")
                )

                # Ignore invalid dataset records
                if not rule_a or not rule_b:
                    continue

                # Check both possible orders
                matched = (
                    (
                        ingredient_a == rule_a
                        and ingredient_b == rule_b
                    )
                    or
                    (
                        ingredient_a == rule_b
                        and ingredient_b == rule_a
                    )
                )

                if not matched:
                    continue

                # ==================================
                # IMPORTANT:
                # SAFE IS NOT A CONFLICT
                # ==================================

                severity = str(
                    conflict.get(
                        "severity",
                        ""
                    )
                ).strip().lower()

                if severity == "safe":
                    continue

                # Prevent duplicate pairs
                key = tuple(
                    sorted(
                        [
                            rule_a,
                            rule_b
                        ]
                    )
                )

                if key in seen:
                    continue

                seen.add(key)

                found_conflicts.append(
                    conflict
                )

        return found_conflicts

    # ==========================================
    # COMPARE TWO PRODUCTS
    # ==========================================

    def compare_products(
        self,
        product1,
        product2
    ):

        conflicts = []

        # ==========================================
        # NORMALIZE PRODUCT 1
        # ==========================================

        product1 = [
            normalize_ingredient(ingredient)
            for ingredient in product1
            if ingredient
        ]

        product1 = list(
            set(
                ingredient
                for ingredient in product1
                if ingredient
            )
        )

        # ==========================================
        # NORMALIZE PRODUCT 2
        # ==========================================

        product2 = [
            normalize_ingredient(ingredient)
            for ingredient in product2
            if ingredient
        ]

        product2 = list(
            set(
                ingredient
                for ingredient in product2
                if ingredient
            )
        )

        # ==========================================
        # TRACK DUPLICATE CONFLICTS
        # ==========================================

        seen = set()

        # ==========================================
        # COMPARE EVERY PRODUCT 1 INGREDIENT
        # WITH EVERY PRODUCT 2 INGREDIENT
        # ==========================================

        for ingredient_a in product1:

            for ingredient_b in product2:

                for conflict in self.conflicts:

                    rule_a = normalize_ingredient(
                        conflict.get(
                            "ingredient_1",
                            ""
                        )
                    )

                    rule_b = normalize_ingredient(
                        conflict.get(
                            "ingredient_2",
                            ""
                        )
                    )

                    # Ignore invalid rules
                    if not rule_a or not rule_b:
                        continue

                    # ==================================
                    # CHECK BOTH ORDERS
                    # ==================================

                    matched = (
                        (
                            ingredient_a == rule_a
                            and ingredient_b == rule_b
                        )
                        or
                        (
                            ingredient_a == rule_b
                            and ingredient_b == rule_a
                        )
                    )

                    if not matched:
                        continue

                    # ==================================
                    # GET SEVERITY
                    # ==================================

                    severity = str(
                        conflict.get(
                            "severity",
                            ""
                        )
                    ).strip().lower()

                    # ==================================
                    # IMPORTANT:
                    # SAFE INTERACTIONS ARE NOT
                    # CONFLICTS
                    # ==================================

                    if severity == "safe":
                        continue

                    # ==================================
                    # ONLY ACCEPT REAL SEVERITIES
                    # ==================================

                    if severity not in [
                        "low",
                        "medium",
                        "high"
                    ]:
                        continue

                    # ==================================
                    # CREATE UNIQUE PAIR KEY
                    # ==================================

                    key = tuple(
                        sorted(
                            [
                                rule_a,
                                rule_b
                            ]
                        )
                    )

                    # Avoid duplicate conflicts
                    if key in seen:
                        continue

                    seen.add(key)

                    conflicts.append(
                        conflict
                    )

        return conflicts

    # ==========================================
    # CALCULATE OVERALL SEVERITY
    # ==========================================

    def calculate_overall_severity(
        self,
        conflicts
    ):

        # No conflicts
        if not conflicts:
            return "safe"

        severities = [
            str(
                conflict.get(
                    "severity",
                    ""
                )
            ).strip().lower()
            for conflict in conflicts
        ]

        # ==========================================
        # HIGH HAS HIGHEST PRIORITY
        # ==========================================

        if "high" in severities:
            return "high"

        # ==========================================
        # MEDIUM
        # ==========================================

        if "medium" in severities:
            return "medium"

        # ==========================================
        # LOW
        # ==========================================

        if "low" in severities:
            return "low"

        # ==========================================
        # FALLBACK
        # ==========================================

        return "safe"

    # ==========================================
    # GET STATUS
    # ==========================================

    def get_status(
        self,
        conflicts_or_severity
    ):

        # If a conflict list is provided
        if isinstance(
            conflicts_or_severity,
            list
        ):

            severity = (
                self.calculate_overall_severity(
                    conflicts_or_severity
                )
            )

        else:

            severity = str(
                conflicts_or_severity
            ).strip().lower()

        # ==========================================
        # HIGH
        # ==========================================

        if severity == "high":
            return "WARNING"

        # ==========================================
        # MEDIUM
        # ==========================================

        if severity == "medium":
            return "CAUTION"

        # ==========================================
        # LOW
        # ==========================================

        if severity == "low":
            return "CAUTION"

        # ==========================================
        # SAFE
        # ==========================================

        return "SAFE"


    def analyze(self, ingredients):
                    conflicts = self.check_conflicts(ingredients)

                    return {
                            "ingredients": ingredients,
                            "conflict_count": len(conflicts),
                            "conflicts": conflicts,
                            "overall_severity": self.calculate_overall_severity(conflicts),
                            "status": self.get_status(conflicts)
                    }