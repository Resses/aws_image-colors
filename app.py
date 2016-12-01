from flask import Flask, request
import requests
import tempfile
import subprocess
from PIL import Image
from io import BytesIO
from werkzeug.contrib.cache import MemcachedCache
cache = MemcachedCache(['127.0.0.1:11211'])


app = Flask(__name__)

@app.route("/")
def index():
    # if user goes to index, give them the url
    return "Hey there! Use /api/num_colors/src=<imageurl> to get the number of colors in your image"

@app.route("/api/num_colors")
def get_num_colors():
    try:
        # get the image url from the src parameter
        image_url = request.args.get('src')
        rv = cache.get(image_url)
        if rv is None:
            # use requsets to get the image from the url.
            r = requests.get(image_url)
            img = Image.open(BytesIO(r.content))
            # save the image in a temporary file
            temp_file_name = tempfile.NamedTemporaryFile().name
            img.save(temp_file_name, 'png')
            # subprocess allows to make command line call
            # use imagemagick command to get the number of colors in the image
            num_colors = subprocess.Popen('identify -format %k ' + temp_file_name, shell= True, stdout=subprocess.PIPE)
            rv = num_colors.stdout.read()
            cache.set(image_url, rv)
        return rv
    except:
        return "Something went wrong. Please check that your url includes an src parameter with a valid image file name"
if __name__ == "__main__":
    app.run(host='0.0.0.0')
