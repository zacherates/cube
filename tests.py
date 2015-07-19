import itertools
import re

from nose.tools import *

import build

db = build.CardDB.default()

cards = [
	('Hill Giant', ['Red'], 'Mono-vanilla'),
	('Unburial Rites', ['White', 'Black'], 'Off color activation'),
	('Yasova Dragonclaw', ['Blue', 'Red', 'Green'], 'Hybrid activation'),
	('Basilica Screecher', ['Black'], 'Reminder text doesn\'t count'),
	('Gust-Skimmer', ['Blue'], 'Off-color artifact'),
	('Savage Lands', [], 'Lands have their own section and are balanced seperately)'),
]

	

def test_color_identity():
	def check_color_identity((name, colors, message)):
		card = db.get_card(name)
		eq_(card.colors, colors, message)

	for case in cards:
		yield check_color_identity, case

def matches(actual, pattern):
	assert re.match(pattern, actual), "{0} ~= {1}".format(actual, pattern)


def test_attrs():
	giant = db.get_card("Hill Giant")
	assert 'Creature' in giant.types
	assert 'Hill Giant' == giant.name
	assert 802 == giant.multiverseid
	assert 4 == giant.cmc

	matches(giant.url, r"^http://gatherer.wizards.com/Pages/Card/Details\.aspx\?multiverseid=\d+$")
	matches(giant.image_url, r"^http://gatherer.wizards.com/Handlers/Image\.ashx\?multiverseid=\d+&type=card$")

sloppy_names = [
	('Hull Giant', 'Hill Giant'),
	('Rust Kimmer', 'Gust-Skimmer'),
]

def test_find_sloppy():
	def check_find_sloppy((sample, corrected_to)):
		card = db.get_card_sloppy(sample)
		eq_(card.name, corrected_to)

	for case in sloppy_names:
		yield check_find_sloppy, case

def test_iter():
	sample = list(itertools.islice(db, 10))
	eq_(len(sample), 10)
	print sample[0], build.Card
	assert isinstance(sample[0], build.Card)


	
