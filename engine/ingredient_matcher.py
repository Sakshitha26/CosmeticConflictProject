import difflib

# Master ingredient list
KNOWN_INGREDIENTS = [
    "AQUA",
    "WATER",
    "GLYCERIN",
    "NIACINAMIDE",
    "RETINOL",
    "SALICYLIC ACID",
    "VITAMIN C",
    "HYALURONIC ACID",
    "CETEARYL ALCOHOL",
    "CETYL ALCOHOL",
    "STEARYL ALCOHOL",
    "PROPYLENE GLYCOL",
    "GLYCOLIC ACID",
    "LACTIC ACID",
    "BENZOYL PEROXIDE",
    "DIMETHICONE",
    "PANTHENOL",
    "TOCOPHEROL",
    "FRAGRANCE",
    "PARFUM",
    "SODIUM HYALURONATE"
]


def match_ingredients(ingredients):

    matched = []

    for ingredient in ingredients:

        result = difflib.get_close_matches(
            ingredient,
            KNOWN_INGREDIENTS,
            n=1,
            cutoff=0.5
        )

        if result:
            matched.append(result[0])
        else:
            matched.append(ingredient)

    return matched