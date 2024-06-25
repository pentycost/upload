from flask import Flask, request, render_template, redirect, url_for, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 300 * 1024 * 1024  # Set max upload size to 300 MB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///videos.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100), nullable=False)
    gallery = db.Column(db.Integer, nullable=False)  # Gallery number (1 to 8)

# Recreate the database
with app.app_context():
    db.drop_all()  # Remove existing tables
    db.create_all()  # Create tables with updated schema


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        gallery = request.form.get('gallery')
        if file and file.filename != '' and gallery in [str(i) for i in range(1, 9)]:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            new_video = Video(filename=filename, gallery=int(gallery))
            db.session.add(new_video)
            db.session.commit()
            return redirect(url_for('gallery', gallery=gallery))
    return render_template('upload.html')

@app.route('/gallery/<int:gallery>')
def gallery(gallery):
    videos = Video.query.filter_by(gallery=gallery).all()
    return render_template(f'{gallery}.html', videos=videos)

@app.route('/uploads/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)
