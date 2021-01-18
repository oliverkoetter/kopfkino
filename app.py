import os
from flask import Flask, request, send_from_directory, abort, jsonify
import moviepy
import datetime
import requests
from pathlib import Path
from pexels_api import API
import pyttsx3

app = Flask(__name__)

#custom functions
def dl_img (url, filename):
    r = requests.get(url, allow_redirects=True)
    open(filename, 'wb').write(r.content)


def zoom(file, t):
    f = (ImageClip(file)
            .resize(height=screensize[1])
            .resize(lambda t: 1 + 0.02 * t)
            .set_position(('center', 'center'))
            .set_duration(t)
            )
    return f


def resizeToOutputSize(f):
    if (f.w < WIDTH_OUT):
        f = f.resize(width = WIDTH_OUT)
    if (f.h < HEIGHT_OUT):
        f = f.resize(height = HEIGHT_OUT)
    f = f.crop( x_center=f.w/2, y_center=f.h/2, width = WIDTH_OUT, height = HEIGHT_OUT)
    return f

'''
def overlayText(text, t):
    overlay = TextClip(text,
                       size=(WIDTH_OUT, HEIGHT_OUT),
                       color=FONT_COLOUR,
                       method="caption",
                       align="center",
                       fontsize=(FONTSIZE_MAIN),
                       font=FONT
                       )
    overlay = overlay.set_duration(t)
    return overlay


def overlayAttribution(text, t):
    attribution = TextClip(text,
                           size=(WIDTH_OUT, FONTSIZE_SUB),
                           color="white",
                           fontsize=(FONTSIZE_SUB),
                           align="center",
                           method="caption",
                           font="Helvetica"
                           )
    attribution = attribution.set_duration(t)
    attribution = attribution.set_position((0, 0.95), relative=True)
    return attribution
'''

#configurations of paths, output URL, file structure
#16:9 ratios possible for upright smartphone usage
#540, 960 creates 1/4 data size compared to FullHD
WIDTH_OUT = 540
HEIGHT_OUT = 960
screensize = (WIDTH_OUT, HEIGHT_OUT)

FONT = "Helvetica-Bold"
FONTSIZE_MAIN = WIDTH_OUT*0.05
FONTSIZE_SUB = WIDTH_OUT*0.03
FONT_COLOUR = "black"
PADDING = WIDTH_OUT * 0.1

readingSpeed = 0.2
search_words = [
				"tree",
				"dog",
				"sun",
				"wind",
				"beach"
				]


suffix = datetime.datetime.now().strftime("%y%m%d_%H%M%S")
ABS_PATH = os.path.abspath(__file__) #"/app.py"
BASE_DIR = os.path.dirname(ABS_PATH) #"/"

Path(os.path.join(BASE_DIR, "uploads", suffix)).mkdir(parents=True, exist_ok=True)
INPUT = os.path.join(BASE_DIR, "uploads", suffix)
Path(os.path.join(BASE_DIR, "downloads", suffix)).mkdir(parents=True, exist_ok=True)
OUTPUT = os.path.join(BASE_DIR, "downloads", suffix)

OUTPUT_NAME = "Kopfkino"
OUPUT_URL = ""

FILENAME = "_".join([OUTPUT_NAME, suffix]) # e.g. 'mylogfile_120508_171442'


# Pexels API setup
PEXELS_API_KEY = "563492ad6f91700001000001d9cd85bd0c064a838dea391c8a73211c"
api = API(PEXELS_API_KEY)

# flask setup
# available routes:
# /create/<JSON file with following parameters>
'''
{
	„user_input“ : „<text, max ### characters>“,
	„style“: „serious or emotional or promo“,
	„VoiceOver“: „<True or False>“
}
'''

@app.route("/")
def hello_world():
	return "Hello Index!"

#TESTING
@app.route('/dl/<path:filename>', methods=['GET', 'POST'])
def download(filename):
	return send_from_directory(directory=OUTPUT, filename=filename, as_attachment=True)

@app.route('/up/<filename>', methods=['POST'])
def upload(filename):
	"""Upload a file to normal directory"""

	if "/" in filename:
		# Return 400 BAD REQUEST
		abort(400, "no subdirectories allowed")

	with open(os.path.join(INPUT, os.path.join(OUTPUT, FILENAME)), "wb") as fp:
		fp.write(request.data)

	# Return 201 CREATED
	return "", 201


# KOPFKINO ROUTING
@app.route('/create/<string:data>', methods=['GET'])
def create(data):
    input = data
    print("received via GET request: ", data)
    i = 1
#    try:
    api.search(search_words[i], page=1, results_per_page=2)
    ph = api.get_entries()
    print(ph)
    dl_img(ph[0].large, os.path.join(OUTPUT, str(FILENAME + ".jpg")))
    print("successfull API fetch, file was written")
#    except:
#        print("ERROR!!!! Suchwort konnte nicht gefunden werden. Platzhalter wird eingesetzt!")
    return send_from_directory(directory=OUTPUT, filename=str(FILENAME + ".jpg"), as_attachment=True)

# KOPFKINO PROCESSING


if __name__ == "__main__":
	app.run(debug=True, threaded=True)












