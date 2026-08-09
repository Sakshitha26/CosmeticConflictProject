import re
import json
import os
from difflib import SequenceMatcher


# ============================================================
# KNOWN COSMETIC INGREDIENTS
# ============================================================

KNOWN_INGREDIENTS = [
    "retinol",
    "salicylic acid",
    "salicylic",
    "vitamin c",
    "ascorbic acid",
    "benzoyl peroxide",
    "niacinamide",
    "ceramide",
    "ceramides",
    "glycerin",
    "glycerine",
    "hyaluronic acid",
    "sodium hyaluronate",
    "vitamin e",
    "tocopherol",
    "tocopheryl acetate",
    "squalane",
    "zinc oxide",
    "titanium dioxide",
    "glycolic acid",
    "lactic acid",
    "azelaic acid",
    "adapalene",
    "cetearyl alcohol",
    "cetyl alcohol",
    "stearyl alcohol",
    "benzyl alcohol",
    "phenoxyethanol",
    "ethylhexylglycerin",
    "ethylhexyl palmitate",
    "glyceryl stearate",
    "potassium hydroxide",
    "sodium hydroxide",
    "sodium benzoate",
    "potassium sorbate",
    "citric acid",
    "fragrance",
    "parfum",
    "dimethicone",
    "cyclopentasiloxane",
    "polysorbate 20",
    "polysorbate 80",
    "carbomer",
    "xanthan gum",
    "allantoin",
    "panthenol",
    "caffeine",
    "urea",
    "propylene glycol",
    "butylene glycol",
    "pentylene glycol",
    "propanediol",
    "caprylyl glycol",
    "caprylic acid",
    "capric acid",
    "caprylic triglyceride",
    "coconut oil",
    "jojoba oil",
    "sunflower seed oil",
    "argan oil",
    "mineral oil",
    "olive oil",
    "castor oil",
    "shea butter",
    "sodium citrate",
    "lecithin",
    "cholesterol",
    "silica",
    "algae extract",
    "cucumber extract",
    "green tea extract",
    "aloe vera",
    "aloe barbadensis",
    "tea tree oil",
    "lavender oil",
    "limonene",
    "linalool",
    "geraniol",
    "citronellol",
    "hexyl cinnamal",
    "benzyl salicylate",
    "bht",
    "bha",
    "polysilicone-11",
    "dipotassium glycyrrhizate",
    "sodium citrate",
    "sucrose",
    "copper",
    "magnesium",
    "zinc",
    "kaolin",
    "talc",
    "mica",
    "iron oxide",
    "sodium chloride",
    "potassium chloride",
    "ammonium polyacrylate",
    "polyacrylate",
    "acrylates copolymer",
    "carboxymethyl cellulose",
    "cellulose",
    "hydroxyethylcellulose",
    "hydroxypropyl methylcellulose",
    "glycol",
    "water",
    "aqua"
]


# ============================================================
# LOAD INGREDIENTS FROM DATASET
# ============================================================

def load_dataset_ingredients():

    ingredients = set()

    try:

        base_path = os.path.dirname(
            os.path.dirname(__file__)
        )

        dataset_path = os.path.join(
            base_path,
            "data",
            "dataset_conflicts.json"
        )

        with open(
            dataset_path,
            "r",
            encoding="utf-8"
        ) as file:

            dataset = json.load(file)

        for item in dataset:

            ingredient_1 = str(
                item.get("ingredient_1", "")
            ).lower().strip()

            ingredient_2 = str(
                item.get("ingredient_2", "")
            ).lower().strip()

            if ingredient_1:
                ingredients.add(ingredient_1)

            if ingredient_2:
                ingredients.add(ingredient_2)

    except Exception as e:

        print(
            "WARNING: Could not load dataset ingredients:",
            e
        )

    return ingredients


# ============================================================
# NORMALIZE TEXT
# ============================================================

def normalize_text(text):

    text = text.lower()

    # Common OCR replacements
    text = text.replace("|", " ")
    text = text.replace("\n", " ")
    text = text.replace("\r", " ")
    text = text.replace(",", " ")
    text = text.replace(";", " ")
    text = text.replace(":", " ")
    text = text.replace("(", " ")
    text = text.replace(")", " ")
    text = text.replace("[", " ")
    text = text.replace("]", " ")

    # Keep hyphens because some ingredient names contain them
    text = re.sub(
        r"[^a-z0-9\-\s]",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# ============================================================
# CLEAN SINGLE WORD
# ============================================================

def clean_word(word):

    word = word.lower().strip()

    # Remove unwanted characters
    word = re.sub(
        r"[^a-z0-9\-]",
        "",
        word
    )

    return word


# ============================================================
# FUZZY MATCHING
# ============================================================

def similarity(a, b):

    return SequenceMatcher(
        None,
        a.lower(),
        b.lower()
    ).ratio()


def fuzzy_match_word(word, candidates):

    best_match = None
    best_score = 0.0

    for candidate in candidates:

        # Only compare single words here
        if " " in candidate:
            continue

        score = similarity(
            word,
            candidate
        )

        if score > best_score:

            best_score = score
            best_match = candidate

    # High threshold prevents random OCR words
    # from becoming ingredients
    if best_score >= 0.82:

        return best_match

    return None


# ============================================================
# FUZZY MATCH MULTI-WORD INGREDIENT
# ============================================================

def fuzzy_match_phrase(words, candidates):

    best_match = None
    best_score = 0.0

    max_words = max(
        [
            len(candidate.split())
            for candidate in candidates
            if " " in candidate
        ],
        default=1
    )

    for length in range(
        2,
        max_words + 1
    ):

        if len(words) < length:
            continue

        for i in range(
            len(words) - length + 1
        ):

            phrase = " ".join(
                words[i:i + length]
            )

            for candidate in candidates:

                candidate_words = candidate.split()

                if len(candidate_words) != length:
                    continue

                score = similarity(
                    phrase,
                    candidate
                )

                if score > best_score:

                    best_score = score
                    best_match = candidate

    if best_score >= 0.78:

        return best_match

    return None


# ============================================================
# MAIN INGREDIENT CLEANER
# ============================================================

def clean_ingredients(text):

    if not text:
        return []

    text = normalize_text(text)

    if not text:
        return []

    # --------------------------------------------------------
    # Load ingredients from dataset
    # --------------------------------------------------------

    dataset_ingredients = load_dataset_ingredients()

    all_ingredients = set(
        ingredient.lower().strip()
        for ingredient in KNOWN_INGREDIENTS
    )

    all_ingredients.update(
        dataset_ingredients
    )

    # Remove empty values
    all_ingredients = {
        ingredient
        for ingredient in all_ingredients
        if ingredient
    }

    # --------------------------------------------------------
    # Sort longest ingredients first
    # --------------------------------------------------------

    sorted_ingredients = sorted(
        all_ingredients,
        key=len,
        reverse=True
    )

    found = []

    # --------------------------------------------------------
    # STEP 1
    # Exact matching of complete ingredient names
    # --------------------------------------------------------

    for ingredient in sorted_ingredients:

        pattern = re.escape(
            ingredient
        )

        if re.search(
            r"(?<![a-z])"
            + pattern +
            r"(?![a-z])",
            text
        ):

            if ingredient not in found:

                found.append(
                    ingredient
                )

    # --------------------------------------------------------
    # STEP 2
    # Extract OCR words
    # --------------------------------------------------------

    words = re.findall(
        r"[a-zA-Z][a-zA-Z0-9\-]*",
        text
    )

    words = [
        clean_word(word)
        for word in words
        if len(clean_word(word)) >= 3
    ]

    # --------------------------------------------------------
    # STEP 3
    # Fuzzy match multi-word ingredients
    #
    # Example:
    #
    # "tocopheryl acetete"
    # may match
    # "tocopheryl acetate"
    # --------------------------------------------------------

    multi_word_candidates = [
        ingredient
        for ingredient in all_ingredients
        if " " in ingredient
    ]

    fuzzy_phrases = []

    for length in range(
        2,
        5
    ):

        if len(words) < length:
            continue

        for i in range(
            len(words) - length + 1
        ):

            phrase_words = words[
                i:i + length
            ]

            phrase = " ".join(
                phrase_words
            )

            best_match = None
            best_score = 0.0

            for candidate in multi_word_candidates:

                candidate_words = candidate.split()

                if len(candidate_words) != length:
                    continue

                score = similarity(
                    phrase,
                    candidate
                )

                if score > best_score:

                    best_score = score
                    best_match = candidate

            if (
                best_match
                and best_score >= 0.78
            ):

                fuzzy_phrases.append(
                    (
                        best_match,
                        best_score,
                        i,
                        length
                    )
                )

    # --------------------------------------------------------
    # Add fuzzy multi-word matches
    # --------------------------------------------------------

    fuzzy_phrases.sort(
        key=lambda x: x[1],
        reverse=True
    )

    used_positions = set()

    for (
        ingredient,
        score,
        start,
        length
    ) in fuzzy_phrases:

        positions = set(
            range(
                start,
                start + length
            )
        )

        if positions.intersection(
            used_positions
        ):
            continue

        if ingredient not in found:

            found.append(
                ingredient
            )

        used_positions.update(
            positions
        )

    # --------------------------------------------------------
    # STEP 4
    # Fuzzy match single-word ingredients
    #
    # Example:
    #
    # "nuacinamide"
    #       ↓
    # "niacinamide"
    #
    # "ceramider"
    #       ↓
    # "ceramide"
    # --------------------------------------------------------

    single_word_candidates = [
        ingredient
        for ingredient in all_ingredients
        if " " not in ingredient
    ]

    for index, word in enumerate(words):

        # Ignore words already consumed
        if index in used_positions:
            continue

        match = fuzzy_match_word(
            word,
            single_word_candidates
        )

        if match:

            if match not in found:

                found.append(
                    match
                )

    # --------------------------------------------------------
    # STEP 5
    # Remove partial ingredients
    #
    # Example:
    #
    # cetearyl alcohol
    #
    # should not also produce:
    #
    # cetearyl
    # alcohol
    # --------------------------------------------------------

    final_ingredients = []

    for ingredient in found:

        is_partial = False

        for other in found:

            if ingredient == other:
                continue

            if (
                ingredient in other
                and len(other) > len(ingredient)
            ):

                is_partial = True
                break

        if not is_partial:

            final_ingredients.append(
                ingredient
            )

    # --------------------------------------------------------
    # STEP 6
    # Remove duplicates while preserving order
    # --------------------------------------------------------

    result = []

    for ingredient in final_ingredients:

        if ingredient not in result:

            result.append(
                ingredient
            )

    return result