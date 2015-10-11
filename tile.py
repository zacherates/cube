import json
import os
import re
import shutil
import tempfile

import pytumblr
import grequests
from paver.easy import *

from card_db import CardDB
db = CardDB.from_path("BFZ.json")


client = pytumblr.TumblrRestClient(
  '5B0zCBEOD9NPFqr4U2D2uBhs9UfBbhYyTlNqDN7SWN9b85G0yv',
  'mnQTL22tBorL91nXAbQ7PK9m7A3ss8ddTgKNAFq7SBsKjMwIiE',
  'uf1pcaB3R83uuDEWpCbxhpIHc8UplA111F1Wlq6QkRkKyhSaXp',
  '1RDNpePi4Jptq4ImzstmPSDYUtxxMkRn0SK6EPmcg8tf3FIwdM'
)

def linkify(src):
	def card_link(name):
		card = db.get_card_sloppy(name)
		return '<a href="{0}">{1}</a>'.format(card.url, card.name)

	pattern = re.compile(r"\[([^\]]*)\]")
	return pattern.sub(lambda m: card_link(m.groups()[0]), src) \
				  .replace("\n", "<p>\n")


def main():
	pending = path('posts/pending')
	posted = path('posts/posted')
	for name in os.listdir(pending):
		with open(pending / name) as f:
			post = json.load(f)

		post_id, = re.match("post-(\d+).json", name).groups()
		cards = [db.get_card_by_id(id) for id in post['cards']]

		sh("ssh maenpaa.ca 'python ~/tilify/tilify.py {0} {1}'".format(
			post_id,
			" ".join('"{0}"'.format(card.image_url) for card in cards)
		))

		(_, tiled_image) = tempfile.mkstemp(suffix = ".png")
		sh("scp maenpaa.ca:~/tilify/out/tiled-{0}.png {1}".format(
			post_id,
			tiled_image
		))

		client.create_photo(
			'packonepickone',
			state="queue",
			tags=["mtg", "p1p1", "bfz", "mtgbfz", "limited", "draft"],
			caption = linkify(post['notes']),
			format = "html",
			data = [tiled_image]
		)
		shutil.move(pending / name, posted / name)


if __name__ == "__main__":
	main()
