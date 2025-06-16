from flask import Flask, request, render_template, send_file, redirect, flash, session, url_for
from PIL import Image
import os, io, zipfile
from functools import wraps

app = Flask(__name__)
app.secret_key = 'verander-dit-naar-een-geheim-sleutel'

TOEGANGSCODE = 'wt18'  # Pas deze code aan

tmp_dir = 'tmp'
os.makedirs(tmp_dir, exist_ok=True)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('ingelogd'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        code = request.form.get('code')
        if code == TOEGANGSCODE:
            session['ingelogd'] = True
            return redirect(url_for('index'))
        else:
            flash('Foute code!')
    return render_template('login.html')

@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    if request.method == 'POST':
        files = request.files.getlist('images')
        count = request.form.get('count', type=int)
        if not files or count not in (1, 2, 4):
            flash('Selecteer één of meerdere afbeeldingen en kies 1, 2 of 4.')
            return redirect(request.url)

        zip_buf = io.BytesIO()
        with zipfile.ZipFile(zip_buf, 'w') as zipf:
            for file in files:
                base, _ = os.path.splitext(file.filename)
                img = Image.open(file.stream)
                w, h = img.size
                layouts = {1: (1, 1), 2: (2, 1), 4: (2, 2)}
                cols, rows = layouts[count]
                canvas = Image.new('RGBA', (w * cols, h * rows), (255, 255, 255, 0))
                for i in range(count):
                    x = (i % cols) * w
                    y = (i // cols) * h
                    canvas.paste(img, (x, y))
                img_buf = io.BytesIO()
                canvas.save(img_buf, format='PNG')
                img_buf.seek(0)
                zipf.writestr(f"{base}_{count}.png", img_buf.read())

        zip_buf.seek(0)
        return send_file(
            zip_buf,
            mimetype='application/zip',
            as_attachment=True,
            download_name='duplicated_images.zip'
        )

    return render_template('index.html')

if __name__ == '__main__':
    app.run()