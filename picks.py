import contextlib
import json
import random

from flask import Flask, render_template, send_from_directory, g, request, session
app = Flask(__name__)

import build
import model
from model import Card, Pick, Person

cards = None

@contextlib.contextmanager
def with_db(Session):
	session = Session()
	try:
		yield session
	except:
		session.rollback()
		raise
	else:
		session.commit()
	finally:
		session.close()


def get_card_name(id):
	for card in cards:
		if card.multiverseid == id:
			return card.name

	raise Exception("Invalid card id")

@app.route("/")
def picks():
	return render_template('index.html')

@app.route("/sample")
def sample():
	sample = random.sample(list(cards), 10)
	return render_template("sample.html", sample = sample)

@app.route("/post-picks", methods=["POST"])
def post_picks():
	def unpack((a, b, c)):
		return [(a, b), (a, c), (b, c)]

	def cards(lst):
		def cardify(id):
			card = DB.query(Card).filter_by(multiverse_id = id).first()
			if card:
				return card

			card = Card(multiverse_id=id, name = get_card_name(id))
			DB.add(card)
			DB.commit()
			return card

		return map(cardify, lst)

	
	DB = g.db
	data = request.get_json()
	good = cards(data['good'])
	bad = cards(data['bad'])
	rest = cards(id for id in data['rest'] if id not in good and id not in bad)

	pairs = [] + \
		[(better, worse) for better in good for worse in bad + rest] + \
		[(better, worse) for better in rest for worse in bad] + \
		unpack(good) + unpack(bad)

	for (better, worse) in pairs:
		DB.add(Pick(person_id = g.me.id, better = better.multiverse_id, worse = worse.multiverse_id))

	DB.commit()

	return sample()


@app.route('/media/<path:path>')
def send_js(path):
	return send_from_directory('media', path)

@app.before_first_request
def load_card_db():
	global cards
	cards = build.CardDB.from_path("cards.json")


@app.before_request
def before_request():
	engine, DB = model.connect()
	g.db = DB()

	id = session.get('id', None)
	if id:
		g.me = g.db.query(Person).filter_by(id = id).first()
	else:
		g.me = Person()
		g.db.add(g.me)
		g.db.commit()
		session['id'] = g.me.id


@app.teardown_request
def teardown_request(exception):
	me = getattr(g, 'me', None)
	if me:
		print me.id

	db = getattr(g, 'db', None)
	if db:
		db.close()

if __name__ == "__main__":
	app.debug = True
	app.secret_key = "1234"
	app.run()
