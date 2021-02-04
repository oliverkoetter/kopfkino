import os
import requests

from app import Processing

from moviepy.editor import *
from pexels_api import API
from pathlib import Path
import time
import datetime


# configurations of paths, output URL, file structure
# 16:9 ratios possible for upright smartphone usage
# 540, 960 creates 1/4 data size compared to FullHD
WIDTH_OUT = 540/2
HEIGHT_OUT = 960/2
screensize = (WIDTH_OUT, HEIGHT_OUT)

FONT = "Helvetica-Bold"
FONTSIZE_MAIN = WIDTH_OUT * 0.05
FONTSIZE_SUB = WIDTH_OUT * 0.03
FONT_COLOUR = "pink"
PADDING = WIDTH_OUT * 0.1

readingSpeed = 0.2

source = ["A wonderful serenity has taken possession of my entire soul, like these sweet mornings of spring which I enjoy with my whole heart. I am alone, and feel the charm of existence in this spot, which was created for the bliss of souls like mine. I am so.",
            "One morning, when Gregor Samsa woke from troubled dreams, he found himself transformed in his bed into a horrible vermin. He lay on his armour-like back, and if he lifted his head a little he could see his brown belly, slightly domed and divided by a",
            "The European languages are members of the same family. Their separate existence is a myth. For science, music, sport, etc, Europe uses the same vocabulary. The languages only differ in their grammar, their pronunciation and their most common words.",
            "Far far away, behind the word mountains, far from the countries Vokalia and Consonantia, there live the blind texts. Separated they live in Bookmarksgrove right at the coast of the Semantics, a large language ocean. A small river named Duden flows by their place and supplies it with the necessary regelialia. It is a paradisematic country, in which roasted parts of sentences fly into your mouth.",
            "The bedding was hardly able to cover it and seemed ready to slide off any moment. His many legs, pitifully thin compared with the size of the rest of him, waved about helplessly as he looked. \"What's happened to me?\"",
            "Tons of trash have washed onto Bali's famous Kuta Beach, prompting locals to spend the first day of the new year staging a cleanup. Residents from the Badung area on the Indonesian island cleared 30 tons of marine debris from the beach, according to the state-run Antara news agency. \“Some 70% of the marine debris is plastic waste,\“ Colonel Made Mahaparta from the Udayana Regional Military Command told Antara. The trash was reportedly loaded onto trucks and transported to a landfill site.",
            "There may have been far fewer airplanes in the skies this past year, but if you're looking ahead to future travel, you might take heed of the latest rankings of the world's safest airlines from AirlineRatings.com. AirlineRatings.com keeps tabs on 385 carriers from across the globe, measuring factors including the airlines' crash and serious incident records, and age of their aircraft. \“The challenge this year was the number of airlines that were flying, although our Top 20 safest airlines have all continued to fly or had limited cessation of flights,\“ AirlineRatings editor-in-chief Geoffrey Thomas tells CNN Travel. For 2021, the airline safety and product review website awarded Aussie airline Qantas the top spot.",
            "The coronavirus pandemic transformed the working and social lives of millions of European adults in 2020. Children too have suffered immensely, with months of confinement only giving way to some sense of normality when schools in most countries reopened in the summer and autumn. Now even that is under threat. Students in the UK were due to return from the Christmas break on Monday. But less than a week ago, the government announced the return to school would be delayed by two weeks for almost all high schoolers and some primary (elementary) school children. Learning will move online. On Sunday, Prime Minister Boris Johnson conceded schools may need to close indefinitely.",
            "The potential removal of President Donald Trump from office starts out more popular than any other removal process of a president in recent American history. Removing Trump from office remains quite unpopular among Republicans, however. A look across polls conducted since riots at the Capitol on Wednesday shows that a clear plurality of Americans overall want Trump out of office, even as President-elect Joe Biden is set to be inaugurated on January 20. You can see that well in an ABC News/Ipsos poll released on Sunday. The majority (56%) say Trump should be removed from office, while just 43% believe he should not be removed."
            ]

example = source[len(source)-1]

suffix = datetime.datetime.now().strftime("%y%m%d_%H%M%S")
ABS_PATH = os.path.abspath(__file__)  # "/app.py"
BASE_DIR = os.path.dirname(ABS_PATH)  # "/"

Path(os.path.join(BASE_DIR, "uploads", suffix)).mkdir(parents=True, exist_ok=True)
INPUT = os.path.join(BASE_DIR, "uploads", suffix)
Path(os.path.join(BASE_DIR, "downloads", suffix)).mkdir(parents=True, exist_ok=True)
#OUTPUT = os.path.join(BASE_DIR, "downloads", suffix)
OUTPUT = os.path.join(BASE_DIR, "downloads")

OUTPUT_NAME = "Kopfkino"

audio_dir = "static/music/emotional.mp3"
audio_emotional = AudioFileClip(audio_dir, fps=44100)


# API setups
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
api = API(PEXELS_API_KEY)


def addOne(n):
    return n + 1

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
        img = [
            dl_img(dl[0].large, os.path.join(OUTPUT, str("image_downloaded_" + str(n) + ".jpg"))),
            dl[0].photographer
               ]
        downloaded_files.append(img)
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


def overlay_text(file, t, i):
    overlay = TextClip(file.text_searchwords[i],
                       size=(WIDTH_OUT, HEIGHT_OUT),
                       color=FONT_COLOUR,
                       method="caption",
                       align="North",
                       fontsize=(FONTSIZE_MAIN * 5),
                       )
    combined = CompositeVideoClip([overlay, overlayAttribution(file.downloaded_items[i][1])])
    combined = combined.set_duration(t)
    return combined

def overlayAttribution(text):
    attribution = TextClip(text,
                           size=(WIDTH_OUT, FONTSIZE_SUB),
                           color=FONT_COLOUR,
                           fontsize=(FONTSIZE_SUB),
                           align="center",
                           method="caption",
#                           font="Helvetica"
                           )
    attribution = attribution.set_position((0, 0.95), relative=True)
    return attribution


def create_kopfkino(content, id):
    print(id)
    file = Processing(user_input=content.get("user_input"), style=content.get("style"), voiceover=content.get("voiceover"))
    file.text_searchwords = file.user_input
    print(file.user_input)
    file.downloaded_items = pexels_fetch(file.text_searchwords)
    for i in range(0, len(file.downloaded_items)):
        file.footage.append(zoom(file.downloaded_items[i][0], file.timing[i]))
    for i in range(0, len(file.downloaded_items)):
        clip = overlay_text(file, file.timing[i], i)
        combined = CompositeVideoClip([file.footage[i], clip])
        file.footage_and_text.append(combined)
    file.export_file = concatenate(file.footage_and_text)
    file.export_file = file.export_file.set_audio(audio_emotional.set_duration(file.export_file.duration))
    file.export_file.write_videofile(os.path.join(OUTPUT, f"{id}.mp4"), codec='libx264', audio_codec='aac', fps=24)
    with open(os.path.join(OUTPUT, f"{id}.mp4"), "rb") as trans:
        result = trans.read()
    #return f"Heeeeeelloooooo hier sollte die Datei sein!"
    return result