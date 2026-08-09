import re


def normalize_ingredient(ingredient):

    if not ingredient:
        return ""

    # Convert to lowercase
    ingredient = ingredient.lower()

    # Remove leading and trailing spaces
    ingredient = ingredient.strip()

    # Remove punctuation
    ingredient = re.sub(r"[^\w\s]", "", ingredient)

    # Remove ALL spaces
    # Example:
    # "glycolic acid" -> "glycolicacid"
    # "salicylic acid" -> "salicylicacid"
    ingredient = re.sub(r"\s+", "", ingredient)

    return ingredient