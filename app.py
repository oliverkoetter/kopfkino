import os
from flask import Flask, request, send_from_directory, abort, jsonify
from moviepy.editor import *
import datetime
import requests
from pathlib import Path
from pexels_api import API
#from nltk import sent_tokenize, pos_tag
# import pyttsx3

app = Flask(__name__)


class Processing:
    def __init__(self, user_input, style, voiceover):
        self.user_input = user_input
        self.style = style
        self.voiceover = voiceover
        self.export_filename = "Kopfkino_export_" + str(suffix) + ".mp4"
        self.export_file = None
        self.segments = int
        self.text_segmented = []
        self.text_overlays = []
        self.text_searchwords = []
        self.downloaded_items = []
        self.footage = []
        self.footage_and_text = []
        print(self.footage)
        self.timing = [2 for i in range(10)]
        print(self.timing)


# custom functions
def dl_img(url, filename):
    print(filename)
    r = requests.get(url, allow_redirects=True)
    open(filename, 'wb').write(r.content)
    return filename


def pexels_fetch(to_download):
    downloaded_files = []
    n = 0
    for i in to_download:
        api.search(to_download[n], page=1, results_per_page=1)
        dl = api.get_entries()
        print(dl)
        downloaded_files.append(dl_img(dl[0].large, os.path.join(OUTPUT, str("image_downloaded_" + str(n) + ".jpg"))))
        print(downloaded_files)
        n += 1
    return downloaded_files


def zoom(file, t):
    f = (ImageClip(file)
         .resize(height=screensize[1])
         .resize(lambda t: 1 + 0.02 * t)
         .set_position(('center', 'center'))
         .set_duration(t)
         )
    f = resize_to_ouput_size(f)
#    cvc = ImageClip(f, t)
    return f


def resize_to_ouput_size(f):
    if f.w < WIDTH_OUT:
        f = f.resize(width=WIDTH_OUT)
    if f.h < HEIGHT_OUT:
        f = f.resize(height=HEIGHT_OUT)
    f = f.crop(x_center=f.w / 2, y_center=f.h / 2, width=WIDTH_OUT, height=HEIGHT_OUT)
    return f


def overlay_text(text, t):
    overlay = TextClip(text,
                       size=(WIDTH_OUT, HEIGHT_OUT),
                       color=FONT_COLOUR,
                       method="caption",
                       align="center",
                       fontsize=(FONTSIZE_MAIN),
#                       font=FONT
                       )
    overlay = overlay.set_duration(t)
    return overlay

'''
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

# configurations of paths, output URL, file structure
# 16:9 ratios possible for upright smartphone usage
# 540, 960 creates 1/4 data size compared to FullHD
WIDTH_OUT = 540
HEIGHT_OUT = 960
screensize = (WIDTH_OUT, HEIGHT_OUT)

FONT = "Helvetica-Bold"
FONTSIZE_MAIN = WIDTH_OUT * 0.05
FONTSIZE_SUB = WIDTH_OUT * 0.03
FONT_COLOUR = "black"
PADDING = WIDTH_OUT * 0.1

readingSpeed = 0.2
search_words = [
    "rock",
    "village"
]
'''
search_words = [
    "rock",
    "village",
    "cat",
    "ocean",
    "flower"
]
'''

suffix = datetime.datetime.now().strftime("%y%m%d_%H%M%S")
ABS_PATH = os.path.abspath(__file__)  # "/app.py"
BASE_DIR = os.path.dirname(ABS_PATH)  # "/"

Path(os.path.join(BASE_DIR, "uploads", suffix)).mkdir(parents=True, exist_ok=True)
INPUT = os.path.join(BASE_DIR, "uploads", suffix)
Path(os.path.join(BASE_DIR, "downloads", suffix)).mkdir(parents=True, exist_ok=True)
OUTPUT = os.path.join(BASE_DIR, "downloads", suffix)

audio_dir = "static/music/emotional.mp3"
audio_emotional = AudioFileClip(audio_dir)

OUTPUT_NAME = "Kopfkino"
OUPUT_URL = ""

FILENAME = "_".join([OUTPUT_NAME, suffix])  # e.g. 'mylogfile_120508_171442'

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


# TESTING
@app.route('/dl/<path:filename>', methods=['GET', 'POST'])
def download(filename):
    return send_from_directory(directory=os.path.join(BASE_DIR, "downloads"), filename=filename, as_attachment=True)


@app.route('/up/<filename>', methods=['POST'])
def upload(filename):
    """Upload a file to normal directory"""
    if "/" in filename:
        # Return 400 BAD REQUEST
        abort(400, "no subdirectories allowed")

    with open(os.path.join(INPUT, filename), "wb") as fp:
            fp.write(request.data)

    # Return 201 CREATED
    return "", 201


# KOPFKINO ROUTING
@app.route('/create/<string:data>', methods=['GET'])
def create(data):
    # creating instance of class Processing which bundles all data and pipeline phases
    file = Processing(user_input=data, style="neutral", voiceover=False)
    file.text_searchwords = search_words  # input NLP here
    file.downloaded_items = pexels_fetch(file.text_searchwords)
    for i in range(0, len(file.downloaded_items)):
        file.footage.append(zoom(file.downloaded_items[i], file.timing[i]))
    for i in range(0, len(file.downloaded_items)):
        clip = overlay_text(file.text_searchwords[i], file.timing[i])
        combined = CompositeVideoClip([file.footage[i], clip])
        file.footage_and_text.append(combined)

    file.export_file = concatenate(file.footage_and_text)
    file.export_file = file.export_file.set_audio(audio_emotional.set_duration(file.export_file.duration))
    file.export_file.write_videofile(os.path.join(OUTPUT, file.export_filename), codec='libx264', fps=24)

    return send_from_directory(directory=OUTPUT, filename=file.export_filename, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True, threaded=True)