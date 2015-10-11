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
	assert 'Common' == giant.rarity
	assert not giant.is_basic_land
	assert giant.is_side_a

	also_a_giant = db.get_card_by_id(802)
	assert giant == also_a_giant

	not_a_giant = db.get_card_by_id(803)
	assert not_a_giant != giant

	matches(giant.url, r"^http://gatherer.wizards.com/Pages/Card/Details\.aspx\?multiverseid=\d+$")
	matches(giant.image_url, r"^http://gatherer.wizards.com/Handlers/Image\.ashx\?multiverseid=\d+&type=card$")

	forest = db.get_card("Forest")
	assert forest.is_basic_land

	lily_a = db.get_card("Liliana, Heretical Healer")
	assert lily_a.is_side_a

	lily_b = db.get_card("Liliana, Defiant Necromancer")
	assert not lily_b.is_side_a



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


def test_filters():
	common, = itertools.islice(db.commons, 0, 1)	
	uncommon, = itertools.islice(db.uncommons, 0, 1)	
	rare, = itertools.islice(db.rares, 0, 1)	
	mythic, = itertools.islice(db.mythics, 0, 1)	

	
