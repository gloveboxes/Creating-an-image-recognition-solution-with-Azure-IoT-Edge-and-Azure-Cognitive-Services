
import json
import os
import io
import ptvsd


# Imports for the REST API
from flask import Flask, request

# Imports for image procesing
from PIL import Image
#import scipy
#from scipy import misc

# Imports for prediction
from predict import initialize, predict_image, predict_url

# Allow other computers to attach to ptvsd at this IP address and port, using the secret


# Pause the program until a remote debugger is attached
# ptvsd.wait_for_attach()

app = Flask(__name__)
# app.debug = True

# 4MB Max image size limit
app.config['MAX_CONTENT_LENGTH'] = 4 * 1024 * 1024 

count = 0

# Default route just shows simple text
@app.route('/')
def index():
    return 'CustomVision.ai model host harness'

# Like the CustomVision.ai Prediction service /image route handles either
#     - octet-stream image file 
#     - a multipart/form-data with files in the imageData parameter
@app.route('/image', methods=['POST'])
def predict_image_handler():
    global count
    try:
        print('data received')
        imageData = None
        if ('imageData' in request.files):
            imageData = request.files['imageData']
        else:
            imageData = io.BytesIO(request.get_data())

        #img = scipy.misc.imread(imageData)
        img = Image.open(imageData)
        count = count + 1

        # img.save('/images/image' + str(count) + '.jpg', "JPEG")



        results = predict_image(img)
        return json.dumps(results)
    except Exception as e:
        print('EXCEPTION:', str(e))
        return 'Error processing image', 500


# Like the CustomVision.ai Prediction service /url route handles url's
# in the body of hte request of the form:
#     { 'Url': '<http url>'}  
@app.route('/url', methods=['POST'])
def predict_url_handler():
    try:
        image_url = json.loads(request.get_data())['Url']
        results = predict_url(image_url)
        return json.dumps(results)
    except Exception as e:
        print('EXCEPTION:', str(e))
        return 'Error processing image'

if __name__ == '__main__':
    # Load and intialize the model
    initialize()

    # ptvsd.enable_attach("glovebox", address=('0.0.0.0', 3000))

    # Run the server
    app.run(host='0.0.0.0', port=80)

