import os
from flask import Flask, request, send_from_directory, abort, jsonify
import moviepy

app = Flask(__name__)

dir_down = os.path.join(os.path.dirname(os.path.abspath(__file__)), "downloads/")
dir_up = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads/")
#dir = "/Users/oliverkoetter/PycharmProjects/heroku_test 2/downloads/"

print(dir)
#print(app.config("DOWNLOAD_DIR"))
#print(app.config)

@app.route("/")
def hello_world():
	return "Hello Index!"

@app.route('/dl/<path:filename>', methods=['GET', 'POST'])
def download(filename):
	return send_from_directory(directory=dir_down, filename=filename)

@app.route('/up/<filename>', methods=['POST'])
def upload(filename):
	"""Upload a file to normal directory"""

	if "/" in filename:
		# Return 400 BAD REQUEST
		abort(400, "no subdirectories allowed")

	with open(os.path.join(dir_up, filename), "wb") as fp:
		fp.write(request.data)

	# Return 201 CREATED
	return "", 201

if __name__ == "__main__":
	app.run(debug=True)