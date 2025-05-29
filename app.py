from flask import Flask, request, send_file, render_template_string
from PIL import Image, ImageDraw, ImageFont
import arabic_reshaper
from bidi.algorithm import get_display
import io
import re

app = Flask(__name__)

font_path = "IBMPlexSansArabic-Regular.ttf"
arabic_bg = Image.open("arabic_adha.png")
english_bg = Image.open("english_adha.png")

def is_arabic(text):
    return bool(re.search("[\u0600-\u06FF]", text))

def get_adjusted_font(text, max_width, font_path, max_size=350, min_size=10):
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
        font = get_adjusted_font(name, 1540, font_path)

        if is_arabic(name):
            name = get_display(arabic_reshaper.reshape(name).strip())
            y_offset = 1270
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
        return send_file(img_io, mimetype='image/png')

    return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Create Eid Al Adha Gift Card</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {
            font-family: 'Segoe UI', sans-serif;
            margin: 0;
            padding: 0;
            color: #105171;
        }
        .container {
            background-color: rgba(253, 254, 254, 0.95);
            max-width: 400px;
            margin: 80px auto;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 0 10px rgba(29, 125, 181, 0.3);
        }
        h1 {
            color: #1d7db5;
            text-align: center;
            margin-bottom: 20px;
        }
        label {
            font-weight: bold;
            display: block;
            margin-top: 10px;
        }
        input[type="text"] {
            width: 100%;
            padding: 10px;
            margin-top: 5px;
            border: 1px solid #ccc;
            border-radius: 6px;
        }
        .radio-group {
            margin: 10px 0;
        }
        .radio-group label {
            font-weight: normal;
            margin-right: 10px;
        }
        button {
            width: 100%;
            background-color: #1d7db5;
            color: white;
            border: none;
            padding: 12px;
            border-radius: 6px;
            font-size: 16px;
            margin-top: 20px;
            cursor: pointer;
        }
        button:hover {
            background-color: #105171;
        }
        @media (max-width: 500px) {
            .container {
                margin: 30px 15px;
                padding: 20px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Create Gift Card</h1>
        <form method="post">
            <label for="name">Name:</label>
            <input type="text" name="name" id="name" required>

            <button type="submit">Generate</button>
        </form>
    </div>
</body>
</html>
''')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
