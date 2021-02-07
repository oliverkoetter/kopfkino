import os
from flask import Flask, request, send_from_directory, abort, jsonify
import time
import requests
from pexels_api import API
import redis
from rq import Queue
# import pyttsx3
#import datetime

app = Flask(__name__)
redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
r = redis.from_url(redis_url)
q = Queue(connection=r)

class Processing:
    def __init__(self, user_input, style, voiceover):
        self.user_input = user_input
        self.style = style
        self.voiceover = voiceover
        self.export_filename = f"Kopfkino_export_{666}.mp4"
        self.export_file = None
        self.text_segmented = []
        self.text_segmented = []
        self.text_timing = []
        self.text_overlays = []
        self.text_searchwords = []
        self.downloaded_items = []
        self.footage = []
        self.footage_and_text = []
        self.timing = [3 for i in range(10)]

from tasks import *

# available flask routes:
@app.route("/")
def hello_world():
    return "Hello IndexMindex!"

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



@app.route("/create/", methods=["POST"])
def kopfkino_enqueue_job():
    content = request.get_json()
    job = q.enqueue(create_kopfkino, content)

    return f"https://kopfkino-app.herokuapp.com/{job.id}", 201

@app.route("/<video_id>", methods=["GET"])
def get_final_video(video_id):
    job = q.fetch_job(video_id)
    if job.id in q.finished_job_registry:
        binary_file = open(f"kopfkino_export_job.mp4", "wb")
        binary_file.write(job.result)
        binary_file.close()
        return send_from_directory(directory=os.path.dirname(os.path.realpath(__file__)), filename=f"kopfkino_export_job.mp4", as_attachment=True), 200
    elif job.id in q.failed_job_registry:
        return "There is a problem with the processing, please try again!", 500
    else:
        return "Please wait, file (not yet) created", 404

@app.route("/nlp/", methods=["GET", "POST"])
def nlp_2():
    content = request.get_json()
    file = Processing(user_input=content.get("user_input"), style=content.get("style"),
                      voiceover=content.get("voiceover"))
    
    job = q.enqueue(nlp_testing_2, file)
    
    while job.id not in q.finished_job_registry:
        time.sleep(0.1)
        
    return f"Ergebnis für Funktion nlp_testing_2: {job.result}", 201

if __name__ == "__main__":
    app.run(threaded=True)
