import contextlib
import collections
import json
import random

from flask import Flask, render_template, send_from_directory, g, request, session
app = Flask(__name__)

import build
import model
from model import Card, CardToTag, Pick, Person, Tag, Tier, TierToCard

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
	return get_card(id).name

def get_card(id):
	for card in cards:
		if card.multiverseid == id:
			return card

	raise Exception("Invalid card id")

@app.route("/")
def picks():
	return render_template('index.html')

def sql(db, query, *args):
	return db.connection().execute(query, *args)

def picked(db, person_id):
	results = sql(db, '''
		select better from pick where person_id = ?
		union
		select worse from pick where person_id = ?
	''', person_id, person_id)
	return [int(result) for result, in results]

@app.route("/sample")
def sample():
	already_picked = picked(g.db, g.me.id)
	candidates = [card for card in cards 
			if card.multiverseid not in already_picked]

	sample = random.sample(candidates, 10)
	return render_template("sample.html",
		rated = len(already_picked),
		sample = sample,
		total = len(list(cards)),
	)

def cards_by_tier(db, person_id):
	results = sql(db, '''
		select card, description from tier, tier_to_card 
		where person_id = ? and tier_id = tier.id
	''', person_id)

	by_tier = collections.defaultdict(list)
	for id, tier in results:
		card = get_card(int(id))
		by_tier[tier].append(card)

	return by_tier

def load_tags(db, person_id):
	results = sql(db, '''
		select card, name from tag, card_to_tag
		where tag.id = tag_id and person_id = ?
	''', person_id)

	tags_by_card = collections.defaultdict(list)
	for card, tag in results:
		tags_by_card[int(card)].append(tag)

	return tags_by_card

class Comparisons(object):
	def __init__(self):
		self.better_than = []
		self.worse_than = []

def load_comparisons(db, person_id):
	results = sql(db, '''
		select better, worse from pick where person_id = ?			
	''', person_id)


	results = collections.defaultdict(Comparisons)
	for better, worse in results:
		better, worse = int(better), int(worse)
		results[better].better_than.append(worse)
		results[worse].worse_than.append(better)

	return results


@app.route("/pick_order_list")
def pick_order_list():
	def account_for_rarity(card, rating):
		if card.rarity == "Common":
			return min(2.999, rating)

		if card.rarity == "Uncommon":
			return min(3.999, rating)

		return rating

	def account_for_cards_rated_higher(card, rating):
		better_ids = comparisons[card.multiverseid].worse_than
		if not better_ids:
			return rating

		betters = [get_card(id) for id in better_ids]
		ceiling = min(rate(better) for better in betters) - 0.001
		return min(ceiling, rating)
		

	def rate(card):
		tags = tags_by_card[card.multiverseid]
		exp =  3 if "1st" in tags else \
			   2 if "2nd" in tags else \
			   1 if "3rd" in tags else \
			  -1 if "bad" in tags else \
			   0
			  	
		rating = 1.5 + (1.00 * exp)
		rating = account_for_rarity(card, rating)
		rating = account_for_cards_rated_higher(card, rating)
		return rating

	def section(lower, upper):
		return [card for rating, card in rated if lower <= rating < upper]

	comparisons = load_comparisons(g.db, g.me.id)
	tags_by_card = load_tags(g.db, g.me.id)
	rated = sorted(((rate(card), card) for card in cards), reverse = True)
	for rating, card in rated:
		print card.name.encode('latin-1'), rating

	return render_template("pick_order_list.html",
		sections = [
			("The Best of the Best", section(4, 5)),
			("The Best Uncommons and Good Rares", section(3, 4)),
			("The Best Commons and Good Uncommons", section(2, 3)),
			("Playable", section(1, 2)),
			("Chaff", section(0, 1)),
		]
	)

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

	def tier(name):
		tier = Tier(person_id = g.me.id, description = name)
		DB.add(tier)
		return tier

	def tag(tag, cards):
		for card in cards:
			DB.add(CardToTag(tag_id = tag.id, card = card.multiverse_id, person_id = my_id))

	DB = g.db
	my_id = g.me.id
	tags = get_tags(DB)
	DB.commit()

	data = request.get_json()
	good = cards(data['good'])
	bad = cards(data['bad'])
	rest = cards(id for id in data['rest'] if id not in data['good'] and id not in data['bad'])

	tag(tags['good'], good)
	tag(tags['bad'], bad)
	tag(tags['rest'], rest)
	tag(tags['1st'], [good[0]])
	tag(tags['2nd'], [good[1]])
	tag(tags['3rd'], [good[2]])



	pairs = [] + \
		[(better, worse) for better in good for worse in bad + rest] + \
		[(better, worse) for better in rest for worse in bad] + \
		unpack(good) + unpack(bad)

	for (better, worse) in pairs:
		DB.add(Pick(person_id = g.me.id, better = better.multiverse_id, worse = worse.multiverse_id))

	DB.commit()

	return sample()


def get_tags(db):
	results = {}
	for tag in db.query(Tag):
		results[tag.name] = tag

	return results

@app.route('/media/<path:path>')
def send_js(path):
	return send_from_directory('media', path)

@app.before_first_request
def load_card_db():
	global cards
	cards = [card for card in build.CardDB.from_path("cards.json")
				if not card.is_basic_land and card.is_side_a]

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
