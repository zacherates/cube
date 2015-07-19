import random

from flask import Flask, render_template, send_from_directory
app = Flask(__name__)

import build

cards = None

@app.route("/")
def picks():
	return render_template('index.html')

@app.route("/sample")
def sample():
	sample = random.sample(list(cards), 10)
	return render_template("sample.html", sample = sample)


@app.route('/media/<path:path>')
def send_js(path):
    return send_from_directory('media', path)

@app.before_first_request
def load_card_db():
	global cards
	cards = build.CardDB.from_path("cards.json")

if __name__ == "__main__":
	app.debug = True
	app.run()
