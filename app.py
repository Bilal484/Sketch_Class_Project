import cv2
import os
from werkzeug.utils import secure_filename
from flask import Flask, request, render_template

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = "secret key"


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def make_draw_sketch(img):
    # Increase resolution
    scale_percent = 150  # Scale factor for increasing the resolution
    width = int(img.shape[1] * scale_percent / 100)
    height = int(img.shape[0] * scale_percent / 100)
    dim = (width, height)
    high_res_img = cv2.resize(img, dim, interpolation=cv2.INTER_LINEAR)

    # Convert to grayscale
    grayed = cv2.cvtColor(high_res_img, cv2.COLOR_BGR2GRAY)
    # Invert the grayscale image
    inverted = cv2.bitwise_not(grayed)
    # Blur the inverted image
    blurred = cv2.GaussianBlur(inverted, (21, 21), sigmaX=0, sigmaY=0)
    # Create the pencil sketch effect
    sketch = cv2.divide(grayed, 255 - blurred, scale=256)

    # Resize back to original size (optional)
    sketch_resized = cv2.resize(sketch, (img.shape[1], img.shape[0]), interpolation=cv2.INTER_AREA)

    return sketch_resized


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/sketch', methods=['POST'])
def sketch():
    file = request.files['file']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        img = cv2.imread(os.path.join(UPLOAD_FOLDER, filename))
        sketch_img = make_draw_sketch(img)
        sketch_img_name = filename.rsplit('.', 1)[0] + "_sketch.jpg"
        sketch_img_path = os.path.join(app.config['UPLOAD_FOLDER'], sketch_img_name)
        cv2.imwrite(sketch_img_path, sketch_img, [cv2.IMWRITE_JPEG_QUALITY, 95])  # Save the image with high quality
        return render_template('home.html', org_img_name=filename, sketch_img_name=sketch_img_name)


if __name__ == '__main__':
    app.run(debug=True)
