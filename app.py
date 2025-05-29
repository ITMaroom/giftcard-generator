from flask import Flask, request, send_file, render_template_string
from PIL import Image, ImageDraw, ImageFont
import arabic_reshaper
from bidi.algorithm import get_display
import io
import re
import os
import base64

app = Flask(__name__)

PAGE_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Create Eid Gift Card</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {
            font-family: 'Segoe UI', sans-serif;
            background-color: #edeff2;
            margin: 0;
            padding: 0;
        }
        .container {
            max-width: 420px;
            margin: 50px auto;
            padding: 20px;
            background: white;
            border-radius: 12px;
            box-shadow: 0 0 10px rgba(16, 81, 113, 0.2);
        }
        h1 {
            text-align: center;
            color: #1d7db5;
        }
        input[type="text"], button {
            width: 100%;
            padding: 10px;
            margin-top: 10px;
            border-radius: 6px;
            border: 1px solid #ccc;
        }
        button {
            background-color: #1d7db5;
            color: white;
            font-weight: bold;
            border: none;
        }
        button:hover {
            background-color: #105171;
        }

        form input[type="text"], form button {
        width: 100%;
        box-sizing: border-box;
        display: block;
        margin-top: 10px;
        }

        .preview {
            text-align: center;
            margin-top: 20px;
        }
        .preview img {
            width: 100%;
            max-width: 100%;
            border-radius: 8px;
        }
        .download-btn {
            display: block;
            margin: 15px auto 0;
            padding: 10px 20px;
            background-color: #105171;
            color: white;
            border-radius: 6px;
            text-decoration: none;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Create Gift Card With Maroom</h1>
        <form method="post">
            <label for="name">Enter Your Name:</label>
            <input type="text" name="name" id="name" required>
            <button type="submit">Generate</button>
        </form>

        {% if image_url %}
        <div class="preview">
            <h2>Preview</h2>
            <img src="{{ image_url }}" alt="Generated Gift Card">
            <a class="download-btn" href="{{ image_url }}" download="{{ name }}.png">Download Image</a>
        </div>
        {% endif %}
    </div>
</body>
</html>
'''



BASE_DIR = os.path.dirname(os.path.abspath(__file__))
font_path = os.path.join(BASE_DIR, "Bahij_TheSansArabic_Bold.ttf")
arabic_bg = Image.open(os.path.join(BASE_DIR, "Arabic_adha.png"))
english_bg = Image.open(os.path.join(BASE_DIR, "English_adha.png"))


def is_arabic(text):
    return bool(re.search("[\u0600-\u06FF]", text))

def get_adjusted_font(text, max_width, font_path, max_size=330, min_size=10):
    font_size = max_size
    while font_size >= min_size:
        font = ImageFont.truetype(font_path, font_size)
        text_width, _ = ImageDraw.Draw(Image.new("RGB", (1, 1))).textbbox((0, 0), text, font=font)[2:]
        if text_width <= max_width:
            return font
        font_size -= 10
    return ImageFont.truetype(font_path, min_size)

@app.route("/", methods=["GET", "POST"])
def generate_card():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        # lang = request.form.get("lang")
        # img = arabic_bg.copy() if lang == "arabic" else english_bg.copy()
        img = arabic_bg.copy() if is_arabic(name) else english_bg.copy()
        draw = ImageDraw.Draw(img)
        font = get_adjusted_font(name, 1520, font_path)

        if is_arabic(name):
            # name = get_display(arabic_reshaper.reshape(name).strip())
            y_offset = 1280
        else:
            y_offset = 1410

        _, _, text_width, text_height = draw.textbbox((0, 0), name, font=font)
        x = (img.width - text_width) // 2 + 40
        y = (img.height - text_height) // 2 + y_offset

        draw.text((x, y), name, font=font, fill="#f2f3f6")

        # Return image as response
        img_io = io.BytesIO()
        img.save(img_io, 'PNG')
        img_io.seek(0)
        base64_image = base64.b64encode(img_io.read()).decode('utf-8')
        image_data_url = f"data:image/png;base64,{base64_image}"

        return render_template_string(PAGE_HTML, image_url=image_data_url, name=name)

    return render_template_string(PAGE_HTML, image_url=None, name=None)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
