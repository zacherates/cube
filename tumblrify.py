import itertools
import json
import os
import pprint
import sys

import pytumblr
from paver.easy import *

from card_db import CardDB

db = CardDB.from_path("ORI.json")

client = pytumblr.TumblrRestClient(
  '5B0zCBEOD9NPFqr4U2D2uBhs9UfBbhYyTlNqDN7SWN9b85G0yv',
  'mnQTL22tBorL91nXAbQ7PK9m7A3ss8ddTgKNAFq7SBsKjMwIiE',
  'uf1pcaB3R83uuDEWpCbxhpIHc8UplA111F1Wlq6QkRkKyhSaXp',
  '1RDNpePi4Jptq4ImzstmPSDYUtxxMkRn0SK6EPmcg8tf3FIwdM'
)

def fuse(sizes):
	return [sizes['original_size']] + sizes['alt_sizes']

def uploaded_so_far():
	with open('tumblred.json') as f:
		url_data = json.load(f)

	return map(int, url_data.keys())


def update():
	already_uploaded = set(uploaded_so_far())

	root = path('posts/pending')
	for name in os.listdir(root):
		with open(root / name) as f:
			post = json.load(f)

		for card in (db.get_card_by_id(id) for id in post['cards']):
			if card.multiverseid in already_uploaded:
				print "Already uploaded:", card.name
				continue

			client.create_photo('zacherates', state="published", tags=[str(card.multiverseid)], source = card.image_url)
			already_uploaded.add(card.multiverseid)


def main(script, command = None):
	tumblr_urls = {}

	if command == "update":
		update()
		return

	offset = 0
	chunk = 20
	max_post = float("inf")

	for i in itertools.count():
		if max_post < offset * chunk:
			break

		posts = client.posts('zacherates', limit = chunk, offset = offset * chunk)
		pprint.pprint(posts)
		for post in posts['posts']:
			multiverseid = int(post['tags'][0])
			tumblr_urls[multiverseid] = fuse(post['photos'][0])

		offset += 1
		max_post = posts['total_posts']


	pprint.pprint(tumblr_urls)


	with open('tumblred.json', 'w') as out:
		json.dump(tumblr_urls, out)


if __name__ == "__main__":
	main(*sys.argv)
