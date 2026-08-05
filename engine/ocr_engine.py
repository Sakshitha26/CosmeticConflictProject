import re
import pytesseract
from PIL import Image

# Tesseract path
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def extract_text(image_path):
    image = Image.open(image_path)
    return pytesseract.image_to_string(image)


def extract_ingredients(text):

    text = text.upper()

    # Find INGREDIENTS
    start = text.find("INGREDIENTS")

    if start == -1:
        return ""

    text = text[start:]

    # Remove the word INGREDIENTS
    text = re.sub(r"INGREDIENTS[:\s]*", "", text)

    # Stop when common ending words appear
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
        "EXP"
    ]

    end = len(text)

    for word in stop_words:
        pos = text.find(word)
        if pos != -1 and pos < end:
            end = pos

    text = text[:end]

    return text.strip()