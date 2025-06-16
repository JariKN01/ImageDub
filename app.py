import tempfile

from flask import Flask, request, render_template, send_file, redirect, flash
from PIL import Image
import os, io

app = Flask(__name__)
app.secret_key = 'verander-dit-naar-een-geheim-sleutel'

TMP_DIR = 'tmp'
os.makedirs(TMP_DIR, exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files.get('image')
        count = request.form.get('count', type=int)
        if not file or count not in (1, 2, 4):
            flash('Selecteer een afbeelding en kies 1, 2 of 4.')
            return redirect(request.url)

        img = Image.open(file.stream)
        w, h = img.size
        layouts = {1: (1, 1), 2: (2, 1), 4: (2, 2)}
        cols, rows = layouts[count]

        # Maak nieuwe canvas
        nieuw = Image.new('RGBA', (w * cols, h * rows), (255, 255, 255, 0))
        for i in range(count):
            x = (i % cols) * w
            y = (i // cols) * h
            nieuw.paste(img, (x, y))

        # Save naar in-memory buffer
        buf = io.BytesIO()
        nieuw.save(buf, format='PNG')
        buf.seek(0)

        return send_file(
            buf,
            mimetype='image/png',
            as_attachment=True,
            download_name=f'duplicated_{count}.png'
        )

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)