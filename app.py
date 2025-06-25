from flask import Flask, request, render_template, send_file, redirect, flash, session, url_for, send_from_directory, abort
from PIL import Image
import os, io, zipfile
from functools import wraps

# Define the absolute path to your downloads folder
DOWNLOADS_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'downloads')

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


@app.route('/logout', methods=['POST'])
@login_required
def logout():
    session.pop('ingelogd', None)
    flash('Je bent uitgelogd.')
    return redirect(url_for('login'))


@app.route('/wt18', methods=['GET', 'POST'])
@login_required
def wt18():
    if request.method == 'POST':
        files = request.files.getlist('images')
        cols = request.form.get('cols', type=int)
        rows = request.form.get('rows', type=int)

        # Validatie
        if not files or not cols or not rows:
            flash('Selecteer afbeeldingen en kies aantal kolommen en rijen.')
            return redirect(request.url)

        count = cols * rows
        zip_buf = io.BytesIO()
        with zipfile.ZipFile(zip_buf, 'w') as zipf:
            for file in files:
                base, _ = os.path.splitext(file.filename)
                img = Image.open(file.stream)
                w, h = img.size

                # Nieuwe canvasgrootte
                canvas = Image.new('RGBA', (w * cols, h * rows), (255, 255, 255, 0))
                for i in range(count):
                    x = (i % cols) * w
                    y = (i // cols) * h
                    canvas.paste(img, (x, y))

                img_buf = io.BytesIO()
                canvas.save(img_buf, format='PNG')
                img_buf.seek(0)
                zipf.writestr(f"{base}.png", img_buf.read())

        zip_buf.seek(0)
        return send_file(
            zip_buf,
            mimetype='application/zip',
            as_attachment=True,
            download_name='duplicated_images.zip'
        )

    download_filename = 'WT_19_button_rechtsboven_op_foto.zip'
    file_path = os.path.join(DOWNLOADS_FOLDER, download_filename)

    # Check if the file exists
    file_exists = os.path.isfile(file_path)

    return render_template('wt18.html',
                           specific_download=download_filename,
                           file_exists=file_exists)


@app.route('/wt17')
@login_required
def wt17():
    # Specify the filename for this specific page
    download_filename = 'WT_19_button_rechtsboven_op_foto.zip'
    file_path = os.path.join(DOWNLOADS_FOLDER, download_filename)

    # Check if the file exists
    file_exists = os.path.isfile(file_path)

    return render_template('wt17.html',
                           specific_download=download_filename,
                           file_exists=file_exists)

@app.route('/wt19')
@login_required
def wt19():
    # Specify the filename for this specific page
    download_filename = 'WT_19_button_rechtsboven_op_foto.zip'
    file_path = os.path.join(DOWNLOADS_FOLDER, download_filename)

    # Check if the file exists
    file_exists = os.path.isfile(file_path)

    return render_template('wt19.html',
                           specific_download=download_filename,
                           file_exists=file_exists)

@app.route('/wt16')
@login_required
def wt16():
    # Specify the filename for this specific page
    download_filename = 'WT_19_button_rechtsboven_op_foto.zip'
    file_path = os.path.join(DOWNLOADS_FOLDER, download_filename)

    # Check if the file exists
    file_exists = os.path.isfile(file_path)

    return render_template('wt16.html',
                           specific_download=download_filename,
                           file_exists=file_exists)

@app.route('/')
@login_required
def index():
    return render_template('index.html')


@app.route('/downloads/<filename>')
def download_file(filename):
    """Handle file downloads from the downloads folder"""
    file_path = os.path.join(DOWNLOADS_FOLDER, filename)

    # Check if file exists
    if not os.path.isfile(file_path):
        abort(404)

    return send_file(file_path, as_attachment=True)


@app.route('/downloads')
def downloads_page():
    """Display available downloads"""
    try:
        files = os.listdir(DOWNLOADS_FOLDER)
        # Filter only zip files
        zip_files = [f for f in files if f.endswith('.zip')]
        return render_template('downloads.html', files=zip_files)
    except FileNotFoundError:
        # Create downloads folder if it doesn't exist
        os.makedirs(DOWNLOADS_FOLDER, exist_ok=True)
        return render_template('downloads.html', files=[])

if __name__ == '__main__':
    app.run()

