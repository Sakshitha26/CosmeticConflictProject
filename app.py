from flask import Flask, render_template, request
import os
from engine.ingredient_matcher import match_ingredients
from engine.ocr_engine import extract_text, extract_ingredients
from engine.ingredient_cleaner import clean_ingredients

app = Flask(__name__)

# Project directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Upload folder
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():

    if "image" not in request.files:
        return "No image uploaded!"

    image = request.files["image"]

    if image.filename == "":
        return "Please select an image."

    # Save uploaded image
    filename = "uploaded_image.jpg"
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)

    image.save(filepath)

    try:
        # Step 1: OCR
        text = extract_text(filepath)

        # Step 2: Extract Ingredients Section
        ingredients_text = extract_ingredients(text)

        # Step 3: Clean Ingredients
        ingredients = clean_ingredients(ingredients_text)
        matched_ingredients = match_ingredients(ingredients)
        # Convert list to HTML
        ingredient_list = ""

        for ingredient in ingredients:
            ingredient_list += f"<li>{ingredient}</li>"

        return f"""
<!DOCTYPE html>
<html>

<head>

<title>Cosmetic Conflict Analyzer</title>

<style>

body {{
    font-family: Arial;
    background: #f5f5f5;
    padding: 40px;
}}

.container {{
    max-width: 900px;
    margin: auto;
    background: white;
    padding: 30px;
    border-radius: 12px;
    box-shadow: 0px 0px 10px rgba(0,0,0,0.2);
}}

h1 {{
    text-align: center;
}}

ul {{
    background: #eeeeee;
    padding: 20px;
    border-radius: 10px;
}}

li {{
    margin-bottom: 8px;
    font-size: 18px;
}}

a {{
    text-decoration: none;
    color: blue;
    font-weight: bold;
}}

</style>

</head>

<body>

<div class="container">

<h1>🧴 Cosmetic Conflict Analyzer</h1>

<h2>Extracted Ingredients</h2>

<ul>

{ingredient_list}

</ul>

<br>

<a href="/">⬅ Upload Another Image</a>

</div>

</body>

</html>

"""

    except Exception as e:
        return f"""
        <h2>OCR Error</h2>
        <p>{e}</p>
        """


if __name__ == "__main__":
    app.run(debug=True)