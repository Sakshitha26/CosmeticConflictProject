import re
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter, ImageOps

# Tesseract path
pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)


def preprocess_image(image):
    """
    Improve small ingredient-label text for OCR.
    """

    # Convert to grayscale
    image = image.convert("L")

    # Make the image much larger
    width, height = image.size
    image = image.resize(
        (width * 4, height * 4),
        Image.Resampling.LANCZOS
    )

    # Increase contrast
    image = ImageEnhance.Contrast(image).enhance(2.5)

    # Sharpen text
    image = image.filter(
        ImageFilter.SHARPEN
    )

    # Auto contrast
    image = ImageOps.autocontrast(image)

    return image


def extract_text(image_path):

    image = Image.open(image_path)

    # Preprocess
    processed = preprocess_image(image)

    # OCR configuration
    config = "--oem 3 --psm 6"

    text = pytesseract.image_to_string(
        processed,
        config=config
    )

    return text


def extract_ingredients(text):

    text = text.upper()

    # Try to find INGREDIENTS
    start = text.find("INGREDIENTS")

    # OCR may read INGREDIENTS incorrectly.
    # If not found, search for common ingredient patterns.
    if start == -1:

        possible_words = [
            "AQUA",
            "WATER",
            "PROPANEDIOL",
            "NIACINAMIDE",
            "GLYCERIN",
            "DIMETHICONE",
            "CERAMIDE"
        ]

        positions = []

        for word in possible_words:
            pos = text.find(word)

            if pos != -1:
                positions.append(pos)

        if positions:
            start = min(positions)
        else:
            return text.strip()

    text = text[start:]

    # Remove INGREDIENTS heading
    text = re.sub(
        r"INGREDIENTS[:\s]*",
        "",
        text
    )

    # Stop at common non-ingredient sections
    stop_words = [
        "DISTRIBUTED",
        "DIRECTIONS",
        "WARNING",
        "CAUTION",
        "MADE IN",
        "NET WT",
        "WWW",
        "BATCH",
        "MFG",
        "EXP",
        "LOT"
    ]

    end = len(text)

    for word in stop_words:

        pos = text.find(word)

        if pos != -1 and pos < end:
            end = pos

    text = text[:end]

    return text.strip()