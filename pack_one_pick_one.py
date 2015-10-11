import codecs
import json
import random
import time

from flask import Flask, render_template, send_from_directory, g, request, session
app = Flask(__name__)

import card_db

cardDb = None

def make_pack():
	has_mythic = random.random() < (1/8.0)
	rare = random.choice(cardDb.mythics if has_mythic else cardDb.rares)
	uncommons = random.sample(cardDb.uncommons, 3)
	commons = random.sample(cardDb.commons, 10)

	return [rare] + uncommons + commons

@app.route("/")
def picks():
	return render_template('pack_one_pick_one.html')

@app.route("/pack")
def pack():
	return render_template("pack.html", pack = make_pack())

@app.route("/post-notes", methods=["POST"])
def post_picks():
	data = request.get_json()
	print data
	post_id = int(time.time() * 10)
	post = 'posts/pending/post-{0}.json'.format(post_id)
	with codecs.open(post, 'a', 'utf-8') as log:
		json.dump(data, log)
		log.write("\n")

	return 'OK'

@app.route('/media/<path:path>')
def send_js(path):
	return send_from_directory('media', path)


@app.before_first_request
def load_card_db():
	global cardDb
	cardDb = card_db.CardDB.from_path("BFZ.json")


if __name__ == "__main__":
	app.debug = True
	app.secret_key = "1234"
	app.run()

