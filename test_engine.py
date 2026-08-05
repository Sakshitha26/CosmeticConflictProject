from engine.conflict_engine import ConflictEngine


engine = ConflictEngine()

ingredients = [
    "RETINOL",
    "Salicylic Acid",
    "Vitamin C",
    "Benzoyl Peroxide"
]

result = engine.analyze(ingredients)


print("Ingredients:")
for ingredient in result["ingredients"]:
    print("-", ingredient)


print("\nConflict Count:", result["conflict_count"])

print("\nConflicts Found:")

for conflict in result["conflicts"]:

    print(
        "\n",
        conflict["ingredient_1"],
        "+",
        conflict["ingredient_2"]
    )

    print("Severity:", conflict["severity"])
    print("Reason:", conflict["reason"])
    print("Recommendation:", conflict["recommendation"])


print("\nOverall Severity:", result["overall_severity"])
print("Status:", result["status"])