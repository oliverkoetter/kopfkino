import os
from flask import Flask, request, send_from_directory, abort, jsonify
from moviepy.editor import *
import datetime
import requests
from pathlib import Path
from pexels_api import API
# import tasks
from nltk import sent_tokenize, pos_tag
# import pyttsx3
import redis
from rq import Queue
import time
from tasks import *
import uuid

app = Flask(__name__)
r = redis.Redis()
q = Queue(connection=r)

class Processing:
    def __init__(self, user_input, style, voiceover):
        self.user_input = user_input
        self.style = style
        self.voiceover = voiceover
        self.export_filename = f"Kopfkino_export_{666}.mp4"
        self.export_file = None
        self.segments = int
        self.text_segmented = []
        self.text_overlays = []
        self.text_searchwords = []
        self.downloaded_items = []
        self.footage = []
        self.footage_and_text = []
        print(self.footage)
        self.timing = [5 for i in range(10)]
        print(self.timing)

'''
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
                       align="North",
                       fontsize=(FONTSIZE_MAIN * 5),
#                       font=FONT
                       )
    overlay = overlay.set_duration(t)
    return overlay

def nlp_pre(user_text):
    return "hello"



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

# available flask routes:
@app.route("/")
def hello_world():
    return "Hello Index!"


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
    return f"Die Datei {filename} wurde erstellt!", 201


# KOPFKINO ROUTING
@app.route('/create/<string:data>', methods=['GET'])
def create(data):
    print(data)
    # creating instance of class Processing which bundles all data and pipeline phases
    file = Processing(user_input=data, style="neutral", voiceover=False)
#    file.text_searchwords = search_words  # input NLP here
    file.text_searchwords = [data]
    file.downloaded_items = pexels_fetch(file.text_searchwords)
    for i in range(0, len(file.downloaded_items)):
        file.footage.append(zoom(file.downloaded_items[i], file.timing[i]))
    for i in range(0, len(file.downloaded_items)):
        clip = overlay_text(file.text_searchwords[i], file.timing[i])
        combined = CompositeVideoClip([file.footage[i], clip])
        file.footage_and_text.append(combined)

    file.export_file = concatenate(file.footage_and_text)
    file.export_file = file.export_file.set_audio(audio_emotional.set_duration(file.export_file.duration))
    file.export_file.write_videofile(os.path.join(OUTPUT, file.export_filename), codec='libx264', audio_codec='aac', fps=24)

    return send_from_directory(directory=OUTPUT, filename=file.export_filename, as_attachment=True)

@app.route("/create/", methods=["POST"])
def create_by_header():
    print(request.is_json)
    content = request.get_json()
    print(content)
    data = [content.get("user_input")]
    print(data)

    # creating instance of class Processing which bundles all data and pipeline phases
    file = Processing(user_input=content.get("user_input"), style=content.get("style"), voiceover=content.get("voiceover"))

    file.text_searchwords = [content.get("user_input")]
    file.downloaded_items = pexels_fetch(file.text_searchwords)

    for i in range(0, len(file.downloaded_items)):
        file.footage.append(zoom(file.downloaded_items[i], file.timing[i]))

    for i in range(0, len(file.downloaded_items)):
        clip = overlay_text(file.user_input, file.timing[i])
        combined = CompositeVideoClip([file.footage[i], clip])
        file.footage_and_text.append(combined)

    file.export_file = concatenate(file.footage_and_text)
    file.export_file = file.export_file.set_audio(audio_emotional.set_duration(file.export_file.duration))
    file.export_file.write_videofile(os.path.join(OUTPUT, file.export_filename), codec='libx264', audio_codec='aac',
                                     fps=24)

    return send_from_directory(directory=OUTPUT, filename=file.export_filename, as_attachment=True), 201

@app.route("/redis/", methods=["POST"])
def background_job_agency():
    content = request.get_json()
    id = uuid.uuid1()
    id = id.int
    job = q.enqueue(create_kopfkino, content, id)

    return f"kopfkino-app.herokuapp.com/{id}"

@app.route("/<video_id>", methods=["GET"])
def get_final_video(video_id):

    return send_from_directory(directory=OUTPUT, filename=f"{video_id}.mp4", as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True, threaded=True)
