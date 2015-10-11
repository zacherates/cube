from __future__ import division

import codecs
import random
import sys

import card_db

BATCH = "alpha"

def make_valid(pack):
	return pack


def main(script, path):
	db = card_db.CardDB.from_path("ORI.json")

	def make_pack():
		has_mythic = random.random() < (1/8.0)
		rare = random.choice(db.mythics if has_mythic else db.rares)
		uncommons = random.sample(db.uncommons, 3)
		commons = random.sample(db.commons, 10)

		return [rare] + uncommons + commons



	with open(path) as f:
		cards = [db.get_card_sloppy(name.strip()) if name.strip() else None for name in f]

	packs = []
	current_pack = []
	for card in cards:
		if card:
			current_pack.append(card)
		else:
			packs.append(current_pack)
			current_pack = []
	
	import pprint
	pprint.pprint(packs)

	with codecs.open("lots-o-packs.txt", "w", "utf-8") as f:
		for i in range(100):
			pack = make_pack()
			for card in pack:
				f.write(u"![{0}]({1})\n".format(card.name, card.image_url))
			f.write("\n\n")




if __name__ == "__main__":
	main(*sys.argv)
