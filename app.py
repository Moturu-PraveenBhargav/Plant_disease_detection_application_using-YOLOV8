from flask import Flask, flash, request, redirect, url_for, render_template
import urllib.request
import os
from werkzeug.utils import secure_filename
import cv2
from ultralytics import YOLO
import torch
from PIL import Image
import io
import shutil
 
app =application = Flask(__name__)
 
UPLOAD_FOLDER = 'static/uploads/'
 
app.secret_key = "mannu@jaanu"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
 
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
 
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
     
 
@app.route('/')
def home():
    return render_template('index.html')
 
@app.route('/', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No image selected for uploading')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        #print('upload_image filename: ' + filename)
        flash('Image successfully uploaded and displayed below')
        img = cv2.imread(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        frame = cv2.imencode('.jpeg', cv2.UMat(img))[1].tobytes()
        image = Image.open(io.BytesIO(frame))
        #perform the detection
        yolo = YOLO('best.pt')
        detections = yolo.predict(image, save = True,save_txt=True)
        #renaming the file

        lst_img= os.listdir(path="runs\\detect\\")[-1]
        change = lst_img+".jpg"
        actual_path = "runs\\detect\\"
        my_dest = change + ".jpg"
        my_source =actual_path +lst_img+'\\'+ "image0.jpg"
        my_dest ="static\\predictions\\"+ change
        os.rename(my_source, my_dest)

        return render_template('index.html', filename=filename)
    else:
        flash('Allowed image types are - png, jpg, jpeg, gif')
        return redirect(request.url)
 
@app.route('/display/<filename>')
def display_image(filename):
    #print('display_image filename: ' + filename)
    return redirect(url_for('static', filename='uploads/' + filename), code=301)

@app.route('/predict')
def result():
    img = os.path.join('static', 'predictions')
    lst_img= os.listdir(path="static/predictions/")[-1]
    file = os.path.join(img, lst_img)
    print(file)
    return render_template('results.html',image=file)
 
if __name__ == "__main__":
    app.run(debug=True)