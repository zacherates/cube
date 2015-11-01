import difflib
import json
import logging
import re

class CardDB(object):
	def __init__(self, sets, logger):
		self.cards = {}
		self.logger = logger

		for expansion in sets:
			for card in sets[expansion]['cards']:
				if 'multiverseid' in card:
					name = card['name']
					self.cards[name] = card

		self.abbreviations = {
			"White": "W",
			"Blue": "U",
			"Black": "B",
			"Red": "R",
			"Green": "G",
			"Land": "L",
			"Colourless": "C",
			"Multi-colour": "M",
		}

		self.abbreviations_reverse = dict((v, k) for (k, v) in self.abbreviations.items())

	def get_card(self, name):
		if "//" in name:
			halves = [self.cards.get(part.strip()) for part in name.split("//")]

			def fuse(name):
				return list(set(halves[0][name] + halves[1][name]))

			return Card({
				'name': name,
				'types': fuse('types'),
				'colors': fuse('colors'),
				'cmc': halves[0]['cmc'] + halves[1]['cmc'],
				'multiverseid': halves[0]['multiverseid']
			}, self)

		card = self.cards.get(name)
		if not card:
			return None
		return Card(card, self)


	def get_card_sloppy(self, name):
		def similarity(a, b):
			return difflib.SequenceMatcher(None, a, b).ratio()
		
		def find_close(name):
			candidates = [(card, similarity(card, name)) for card in self.cards]
			return sorted(candidates, key = lambda (card, p): -p)[0]

		def find_closest():
			close_enough = find_close(name)
			msg =  "Correcting '{0}' --> '{1}'.".format(name, close_enough)
			self.logger.debug(msg)
			return self.get_card(close_enough[0])

		return self.get_card(name) or find_closest()

	def get_card_by_id(self, id):
		for card in self.cards.values():
			if card['multiverseid'] == id:
				return Card(card, self)

		return None

	def __iter__(self):
		return iter(self.get_card(name) for name in self.cards)

	@staticmethod
	def default():
		return CardDB.from_path("AllSets.json")

	@staticmethod
	def from_path(path):
		with open(path) as f:
			sets = json.load(f)

		if 'cards' in sets:
			sets = {'set': sets}

		return CardDB(sets, logging.getLogger("CardDB"))

	def _filter(self, rarity):
		return [card for card in self if card.rarity == rarity]

	@property
	def commons(self):
		return self._filter("Common")

	@property
	def uncommons(self):
		return self._filter("Uncommon")

	@property
	def rares(self):
		return self._filter("Rare")

	@property
	def mythics(self):
		return self._filter("Mythic Rare")

class Card(object):
	def __init__(self, source, db):
		self.source = source
		self.db = db

	def __eq__(self, other):
		return self.multiverseid == other.multiverseid

	def __ne__(self, other):
		return not (self == other)

	def __hash__(self):
		return hash(self.multiverseid)

	@property
	def types(self):
		return self.source.get('types', [])

	@property
	def name(self):
		return self.source.get('name')

	@property
	def multiverseid(self):
		return self.source.get('multiverseid')

	@property
	def cmc(self):
		return self.source.get('cmc', 0)

	@property
	def rarity(self):
		return self.source.get('rarity', None)

	@property
	def is_basic_land(self):
		return self.rarity == "Basic Land"

	@property
	def is_side_a(self):
		return self.source.get('layout', None) != 'double-faced' or \
			self.source.get("number", "").endswith('a')

	@property
	def colors(self):
		def flatten(lst):
			return [item for sublist in lst for item in sublist]

		def WUBRG(colors):
			result = ['White', 'Blue', 'Black', 'Red', 'Green']
			for color in result[:]:
				if color not in colors:
					result.remove(color)
			return result

		def dereminder(text):
			return re.sub(r'\([^(]*\)', '', text)

		if self.is_land():
			return []

		text = dereminder(self.source.get('text', '')) + ' ' + self.source.get('manaCost')
		cost = self.source.get('colors', [])
		patterns = [r"{([WUBRG])}", r"{./([WUBRD])}", r"{([WUBRD])/.}"]
		symbols = flatten(re.findall(pattern, text) for pattern in patterns)
		activations = [self.db.abbreviations_reverse[c] for c in symbols]

		return WUBRG(cost + activations)

	@property
	def image_url(self):
		return "http://gatherer.wizards.com/Handlers/Image.ashx?multiverseid={0}&type=card".format(self.multiverseid)

	@property
	def url(self):
		return "http://gatherer.wizards.com/Pages/Card/Details.aspx?multiverseid={0}".format(self.multiverseid)

	def is_land(self):
		return 'Land' in self.types

	def __str__(self):
		return "<Card '{0}'>".format(self.name)
