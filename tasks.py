import os
import requests
from app import Processing
import nltk
from moviepy.editor import *
from pexels_api import API
from pathlib import Path
import time
import pyttsx3


# configurations of paths, output URL, file structure
# 16:9 ratios possible for upright smartphone usage
# 1080, 1920 --> FullHD resolution
# 540, 960 --> 1/4 data size compared to FullHD
# 270, 480 --> 1/8 data size compared to FullHD
WIDTH_OUT = 540/2
HEIGHT_OUT = 960/2
screensize = (WIDTH_OUT, HEIGHT_OUT)

FONT = "Helvetica-Bold"
FONTSIZE_MAIN = WIDTH_OUT * 0.1
FONTSIZE_SUB = WIDTH_OUT * 0.03
FONT_COLOUR = "white"
PADDING = WIDTH_OUT * 0.1

readingSpeed = 0.2

audio_dir_emotional = "static/music/emotional.mp3"
audio_dir_promo = "static/music/promo.mp3"
audio_dir_neutral = "static/music/neutral.mp3"

audio_emotional = AudioFileClip(audio_dir_emotional, fps=44100)
audio_neutral = AudioFileClip(audio_dir_neutral, fps=44100)
audio_promo = AudioFileClip(audio_dir_promo, fps=44100)


ABS_PATH = os.path.abspath(__file__)  # "/app.py"
BASE_DIR = os.path.dirname(ABS_PATH)  # "/"

Path(os.path.join(BASE_DIR, "downloads")).mkdir(parents=True, exist_ok=True)
OUTPUT = os.path.join(BASE_DIR, "downloads")


# API setups
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
api = API(PEXELS_API_KEY)


def dl_img(url, filename):
    print(filename)
    r = requests.get(url, allow_redirects=True)
    open(filename, 'wb').write(r.content)
    return filename


def pexels_fetch(to_download):
    downloaded_files = []
    n = 0

    for i in to_download:
        api.search(" ".join(i), page=1, results_per_page=1)
        dl = api.get_entries()
        print(dl)
        img = [
            dl_img(dl[0].large, os.path.join(OUTPUT, str("image_downloaded_" + str(n) + ".jpg"))),
            dl[0].photographer
               ]
        downloaded_files.append(img)
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


'''
# voiceover functionality deprecated due to non-existent espeak support on heroku

def voiceover(textSnippet, i):
    engine = pyttsx3.init()
    print(f"inside voiceover func, processing: {textSnippet} \nIsBusy is set to {engine.isBusy()}")
    audioFileName = f"voiceover text segment no. {i}.mp3"
    engine.save_to_file(textSnippet, audioFileName)
    engine.runAndWait()
#    engine.stop()
    print(f"text to speech worked correctly? \nisBusy is set to {engine.isBusy()}")

    return audioFileName
'''


def overlay_text(file, i):
    overlay = TextClip(file.text_segmented[i],
                       size=(WIDTH_OUT * 0.9, HEIGHT_OUT),
                       color=FONT_COLOUR,
                       method="caption",
                       align="East",
                       fontsize=FONTSIZE_MAIN,
                       font=FONT
                       )
    combined = CompositeVideoClip([overlay, overlay_attribution(file.downloaded_items[i][1])])

# voiceover functionality deprecated
#    if file.voiceover == True or file.voiceover == "true" or file.voiceover == "True":
#        audio_clip_temp = AudioFileClip(voiceover(file.text_segmented[i], i), fps=44100)
#        combined = combined.set_audio(audio_clip_temp)

    combined = combined.set_duration(file.text_timing[i])

    return combined


def overlay_attribution(text):
    attribution = TextClip(f"Image from www.pexels.com by: {text}",
                           size=(WIDTH_OUT, HEIGHT_OUT * 0.95),
                           color=FONT_COLOUR,
                           fontsize=FONTSIZE_SUB,
                           align="south",
                           method="caption",
                           font=FONT
                           )
    attribution = attribution.set_position((0, 0.97), relative=True)
    return attribution


def create_kopfkino(content):
    file = Processing(user_input=content.get("user_input"), style=content.get("style"), voiceover=content.get("voiceover"))
    print(f"voiceover from content JSON is set to: {file.voiceover}")
    nlp_testing_2(file)
    print(file.downloaded_items)
    print(file.text_searchwords)
    file.downloaded_items = pexels_fetch(file.text_searchwords)
    
    for i in range(0, len(file.downloaded_items)):
        file.footage.append(zoom(file.downloaded_items[i][0], file.text_timing[i]))
    for i in range(0, len(file.text_segmented)):
        clip = overlay_text(file, i)
        combined = CompositeVideoClip([file.footage[i], clip])
        file.footage_and_text.append(combined)

    file.export_file = concatenate(file.footage_and_text)

    if file.style == "neutral":
        file.export_file = file.export_file.set_audio(audio_neutral.set_duration(file.export_file.duration))
    elif file.style == "emotional":
        file.export_file = file.export_file.set_audio(audio_emotional.set_duration(file.export_file.duration))
    elif file.style == "promo":
        file.export_file = file.export_file.set_audio(audio_promo.set_duration(file.export_file.duration))
    else:
        file.export_file = file.export_file.set_audio(audio_neutral.set_duration(file.export_file.duration))

    file.export_file.write_videofile(os.path.join(OUTPUT, f"Kopfkino_export_in workerinstance.mp4"), codec='libx264',
                                     audio_codec='aac', fps=24)
    with open(os.path.join(OUTPUT, f"Kopfkino_export_in workerinstance.mp4"), "rb") as trans:
        result = trans.read()

    return result


def nlp_testing_2(file):
    text_raw = file.user_input
    print(text_raw)
    file.text_segmented = nltk.sent_tokenize(text_raw)
    for i in range(0, len(file.text_segmented)):
        n = 0
        for c in file.text_segmented[i]:
            n += 1
        n = round(n * readingSpeed, 1)
        if n < 5:
            n = 5
        file.text_timing.append(n)
        text_segmented_to_words = nltk.word_tokenize(file.text_segmented[i])
        file.text_searchwords.append([])
        print(f"POS Tags{nltk.pos_tag(text_segmented_to_words)}")
        for p in nltk.pos_tag(text_segmented_to_words):
            if p[1] in {"JJ", "NN", "NNS", "VB"}:
                print(f"found word {p} and put it to the searchwords")
                file.text_searchwords[i].append(p[0])

    for x in file.text_searchwords:
        if len(x) == 0:
            x.append("error")
            print("-------> ERROR HANDLING NEEDED: No searchword left: appended full sentence OR error")

    return f"\nsegmented: {file.text_segmented}, \ntimings: {file.text_timing} \nsearchwords: {file.text_searchwords}"
