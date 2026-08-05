import re


def clean_ingredients(text):

    text = text.upper()

    # Replace new lines with commas
    text = text.replace("\n", ",")

    # Remove brackets
    text = re.sub(r"[()]", "", text)

    # Split by comma
    ingredients = text.split(",")

    cleaned = []

    for ingredient in ingredients:

        ingredient = ingredient.strip()

        # Ignore very short words
        if len(ingredient) < 3:
            continue

        # Ignore numbers
        if ingredient.isdigit():
            continue

        cleaned.append(ingredient)

    return cleaned