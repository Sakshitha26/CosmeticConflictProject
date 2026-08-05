import re


def normalize_ingredient(ingredient):

    # Convert to lowercase
    ingredient = ingredient.lower()

    # Remove leading and trailing spaces
    ingredient = ingredient.strip()

    # Remove punctuation
    ingredient = re.sub(r"[^\w\s]", "", ingredient)

    # Remove extra spaces
    ingredient = re.sub(r"\s+", " ", ingredient)

    return ingredient