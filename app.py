import os
from flask import Flask, request, render_template, redirect, url_for, flash
from werkzeug.utils import secure_filename
import pandas as pd
import json
import xml.etree.ElementTree as ET

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limite de 16MB

ALLOWED_EXTENSIONS = {'txt', 'csv', 'json', 'xml'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_metadata(filepath):
    filename = os.path.basename(filepath)
    file_size = os.path.getsize(filepath)
    return {'filename': filename, 'size': file_size}

def read_file_content(filepath):
    ext = filepath.rsplit('.', 1)[1].lower()
    if ext == 'txt':
        with open(filepath, 'r', encoding='utf-8') as file:
            return file.read()
    elif ext == 'csv':
        df = pd.read_csv(filepath)
        return df.to_html()
    elif ext == 'json':
        with open(filepath, 'r', encoding='utf-8') as file:
            data = json.load(file)
            return json.dumps(data, indent=4)
    elif ext == 'xml':
        tree = ET.parse(filepath)
        root = tree.getroot()
        return ET.tostring(root, encoding='unicode')
    else:
        return 'Formato de arquivo não suportado.'

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('Nenhum arquivo selecionado.')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('Nenhum arquivo selecionado.')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            metadata = extract_metadata(filepath)
            content = read_file_content(filepath)
            return render_template('index.html', metadata=metadata, content=content)
        else:
            flash('Tipo de arquivo não permitido.')
            return redirect(request.url)
    return render_template('index.html')

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)
