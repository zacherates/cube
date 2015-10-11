import json

class Card:
	def __init__(self, card):
		self.source = card

	@property
	def multiverseid(self):
		return self.source['id']

	@property
	def image_url(self):
		return self.source['url']

	@property
	def rarity(self):
		return self.source['rarity']

class CardDB:
	def __init__(self, cards):
		self.cards = map(Card, cards)

	@staticmethod
	def from_path(path):
		with open(path) as f:
			cards = json.load(f)
			return CardDB(cards)

	def filter(self, rarity):
		return [card for card in self.cards if card.rarity == rarity]

	@property
	def mythics(self):
		return self.filter('Mythic Rare')

	@property
	def rares(self):
		return self.filter('Rare')

	@property
	def uncommons(self):
		return self.filter('Uncommon')

	@property
	def commons(self):
		return self.filter('Common')

	def get_card_by_id(self, multiverseid):
		for card in self.cards:
			if card.multiverseid == multiverseid:
				return card
