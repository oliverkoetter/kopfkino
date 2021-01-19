import os
from flask import Flask, request, send_from_directory, abort, jsonify
from moviepy.editor import *
import datetime
import requests
from pathlib import Path
from pexels_api import API
from nltk import sent_tokenize, pos_tag

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
    "tree",
    "dog",
    "sun",
    "wind",
    "beach"
]

suffix = datetime.datetime.now().strftime("%y%m%d_%H%M%S")
ABS_PATH = os.path.abspath(__file__)  # "/app.py"
BASE_DIR = os.path.dirname(ABS_PATH)  # "/"

Path(os.path.join(BASE_DIR, "uploads", suffix)).mkdir(parents=True, exist_ok=True)
INPUT = os.path.join(BASE_DIR, "uploads", suffix)
Path(os.path.join(BASE_DIR, "downloads", suffix)).mkdir(parents=True, exist_ok=True)
OUTPUT = os.path.join(BASE_DIR, "downloads", suffix)

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

        with open(os.path.join(INPUT, os.path.join(OUTPUT, FILENAME)), "wb") as fp:
            fp.write(request.data)

        # Return 201 CREATED
        return "", 201


# KOPFKINO ROUTING
@app.route('/create/<string:data>', methods=['GET'])
def create(data):
    # creating instance of class Processing which bundles all data and pipeline phases
    file = Processing(["tree", "cat", "dog", "house", "car"], style="neutral", voiceover=False)
    file.text_searchwords = file.user_input # will be taking formdata
    
    file.downloaded_items = pexels_fetch(file.text_searchwords)
    for i in range(0, len(file.downloaded_items)):
        file.footage.append(zoom(file.downloaded_items[i], file.timing[i]))
    file.export_file = concatenate(file.footage)
    file.export_file.write_videofile(os.path.join(OUTPUT, file.export_filename), codec='libx264', fps=24)

    return send_from_directory(directory=OUTPUT, filename=file.export_filename, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True, threaded=True)

'''
##########################################################################################
# KOPFKINO PROCESSING
# improvised version!
examples = ["A wonderful serenity has taken possession of my entire soul, like these sweet mornings of spring which I enjoy with my whole heart. I am alone, and feel the charm of existence in this spot, which was created for the bliss of souls like mine. I am so.",
            "One morning, when Gregor Samsa woke from troubled dreams, he found himself transformed in his bed into a horrible vermin. He lay on his armour-like back, and if he lifted his head a little he could see his brown belly, slightly domed and divided by a",
            "The European languages are members of the same family. Their separate existence is a myth. For science, music, sport, etc, Europe uses the same vocabulary. The languages only differ in their grammar, their pronunciation and their most common words.",
            "Far far away, behind the word mountains, far from the countries Vokalia and Consonantia, there live the blind texts. Separated they live in Bookmarksgrove right at the coast of the Semantics, a large language ocean. A small river named Duden flows by their place and supplies it with the necessary regelialia. It is a paradisematic country, in which roasted parts of sentences fly into your mouth.",
            "The bedding was hardly able to cover it and seemed ready to slide off any moment. His many legs, pitifully thin compared with the size of the rest of him, waved about helplessly as he looked. \"What's happened to me?\"",
            "Tons of trash have washed onto Bali's famous Kuta Beach, prompting locals to spend the first day of the new year staging a cleanup. Residents from the Badung area on the Indonesian island cleared 30 tons of marine debris from the beach, according to the state-run Antara news agency. \“Some 70% of the marine debris is plastic waste,\“ Colonel Made Mahaparta from the Udayana Regional Military Command told Antara. The trash was reportedly loaded onto trucks and transported to a landfill site.",
            "There may have been far fewer airplanes in the skies this past year, but if you're looking ahead to future travel, you might take heed of the latest rankings of the world's safest airlines from AirlineRatings.com. AirlineRatings.com keeps tabs on 385 carriers from across the globe, measuring factors including the airlines' crash and serious incident records, and age of their aircraft. \“The challenge this year was the number of airlines that were flying, although our Top 20 safest airlines have all continued to fly or had limited cessation of flights,\“ AirlineRatings editor-in-chief Geoffrey Thomas tells CNN Travel. For 2021, the airline safety and product review website awarded Aussie airline Qantas the top spot.",
            "The coronavirus pandemic transformed the working and social lives of millions of European adults in 2020. Children too have suffered immensely, with months of confinement only giving way to some sense of normality when schools in most countries reopened in the summer and autumn. Now even that is under threat. Students in the UK were due to return from the Christmas break on Monday. But less than a week ago, the government announced the return to school would be delayed by two weeks for almost all high schoolers and some primary (elementary) school children. Learning will move online. On Sunday, Prime Minister Boris Johnson conceded schools may need to close indefinitely.",
            "The potential removal of President Donald Trump from office starts out more popular than any other removal process of a president in recent American history. Removing Trump from office remains quite unpopular among Republicans, however. A look across polls conducted since riots at the Capitol on Wednesday shows that a clear plurality of Americans overall want Trump out of office, even as President-elect Joe Biden is set to be inaugurated on January 20. You can see that well in an ABC News/Ipsos poll released on Sunday. The majority (56%) say Trump should be removed from office, while just 43% believe he should not be removed."
            ]
search_sentence = examples[len(examples)-1]

print("INPUT: " + search_sentence)

#NLP
#sentencizer
search_sentence_chopped = nltk.sent_tokenize(search_sentence)
ch_count = []
timing = []

i = 0
for sen in search_sentence_chopped:
    ch_count.append(len(search_sentence_chopped[i]))
    i += 1

print(search_sentence)
print(search_sentence_chopped)

#TIMING
i = 0
for ch in ch_count:
#    timing.append(round((int(ch) * readingSpeed), 2))
    x = round((int(ch) * readingSpeed), 2)
    if x < 5:
        x = 5
    timing.append(x)
    #print(timing[i])
    #    print(timing[i])
    i += 1

print(timing)


#video settings

#attribution to stock site
watermark = "pictures by PEXELS.com"

#actual video processing
media = []
jpegs = []
footage = []

#preprocess NLP --> create search queries for Pexels API
choppedSearchwords = []
i = 0
for sen in search_sentence_chopped:
    choppedSearchwords.append([])
    sen = nltk.word_tokenize(sen)
#    print(nltk.pos_tag(sen))
    for p in nltk.pos_tag(sen):
        if p[1] == ("NN" or "NNS" or "NNP" or "NNPS"):
            choppedSearchwords[i].append(p[0])
    i += 1

for s in choppedSearchwords: print(s)




#search on API + downloading in specified resolution --> entering in jpegs array as ready to process files
count = 0
for s in choppedSearchwords:
#    print(api.get_entries())
    try:
        api.search(choppedSearchwords[count][0], page=1, results_per_page=5)
        ph = api.get_entries()
        dl_img(ph[3].large, "image"+ str(count) + ".jpg")
        jpegs.append("image"+ str(count) + ".jpg")
        print("successfull API fetch. file was written index: image" + str(count) + ".jpeg")
    except:
        print("ERROR!!!! Suchwort = --> " + str(s) + "<-- konnte nicht gefunden werden. Platzhalter wird eingesetzt!")
        jpegs.append("error.jpg")
    count += 1

#create footage
i = 0
for file in jpegs:
    img = zoom(file,timing[i])
    img = resize_to_ouput_size(img)
    footage.append(img)
    i += 1

#create text overlay
overlays = []
combined = []
i = 0
for ins in search_sentence_chopped:
    a = overlayText(ins, timing[i])
    b = overlayAttribution(watermark, timing[i])
    c = CompositeVideoClip([footage[i], a.crossfadein(1), b])
    combined.append(c)
    i += 1

# EXPORT experiment
vid = concatenate_videoclips(combined)
vid.write_videofile(os.path.join(OUTPUT, OUTPUT_NAME),codec='libx264', fps=24)

# END of improvised version!
##########################################################################################
'''
