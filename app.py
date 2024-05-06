import os
from flask import Flask, render_template, request, redirect, send_file, url_for
from werkzeug.utils import secure_filename
from pydub import AudioSegment
from PIL import Image
import io

app = Flask(__name__)
#using path absolute
base_dir = os.path.abspath(os.path.dirname(__file__))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/audio-editor')
def audio_editor():
    return render_template('audio.html')

@app.route('/image-editor')
def image_editor():
    return render_template('image.html')

@app.route('/resize', methods=['POST'])
def resize_image():
    if 'image' not in request.files:
        return 'No file uploaded'
    
    file = request.files['image']

    img = Image.open(io.BytesIO(file.read()))
    width, height = img.size

    default_width = width
    default_height = height
    default_rotation_angle = 0


    width = int(request.form['width']) if request.form['width'] else default_width
    height = int(request.form['height']) if request.form['height'] else default_height
    rotation_angle = int(request.form['rotation_angle']) if request.form['rotation_angle'] else default_rotation_angle

    
    if file.filename == '':
        return 'No selected file'
    
    img = Image.open(file)
    resized_img = img.resize((width, height))
    rotated_image = resized_img.rotate(rotation_angle)
    
    save_directory = os.path.join(base_dir, 'static')
    filename = 'resized_image.jpg'
    save_path = os.path.join(save_directory, filename)

    # Save the edited image
    rotated_image.save(save_path)

    return redirect(url_for('resized'))

@app.route('/resized')
def resized():
    return render_template('resized.html')

@app.route('/audio', methods=['POST'])
def audio_compression():
    if request.method == 'POST':
        file = request.files['audio']
        if file:
            file_name = secure_filename(file.filename)
            file_path = os.path.join(base_dir, 'static', file_name) 
            file.save(file_path)  
            audio_io = io.BytesIO()
            audio = AudioSegment.from_mp3(file_path)
            audio.export(audio_io, format='mp3', bitrate='64k')
            os.remove(file_path)
            return send_file(
                audio_io,
                as_attachment=True,
                download_name=f'compressed_{file_name}',
                mimetype='audio/mp3'
            )
        else: 
            return '''
            <h1>File not Found</h1>
        '''
    else:
        return '''
        <h1>Uknown method</h1>
    '''

if __name__ == '__main__':
    app.run(debug=True)
