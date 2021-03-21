# KopfKino - text to video generator
The KopfKino app is an iOS native app, which is currently not (yet) available on the Apple App store. The app lets the user turn a text into a video with upright format on the basis of stock imagery sites (currently included: www.pexels.com).
This project is the back-end for the KopfKino app, tailored for easy setup on a heroku server.

## Installation locally
Make sure all Python dependencies listed in the requirements.txt file are installed via pip. Furthermore ensure that [ImageMagick](https://imagemagick.org/) and [Ghostscript](https://www.ghostscript.com/) are installed for text processing and layout. For proper processing of the queued jobs and the elementary in-memory-database install [Redis](https://redis.io/).

## Installation on heroku
All python dependencies are automatically setup via the requirements.txt. Additional buildpacks need to be added manually, the order is important: 
```
heroku buildpacks:add g2/imagemagick
heroku buildpacks:add sdglhm/heroku-ghostscript-buildpack
heroku buildpacks:add heroku/python
```
The redis server needs to be implemented via the heroku [Redis addon](https://elements.heroku.com/addons/heroku-redis).

## API guide
The microframework used to design this RESTful API is the Flask framework. The available routes on this project are:
### /create/
https://kopfkino-app.herokuapp.com/create/

This route is designed to accept a POST request and a JSON string indicating the three user parameters (user text input, style, voiceover).

###/nlp/
https://kopfkino-app.herokuapp.com/nlp/

This route is also designed to accept a POST request and its purpose is to test the natural language processing in place. The response is the segmented input text.
 
## Maintainers
oliverkoetter (owner)

