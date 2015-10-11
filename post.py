import codecs
import json
import os
import re
import shutil
import sys
import time

import jinja2
from paver.easy import *
import pytumblr

from card_db import CardDB

db = CardDB.from_path("ORI.json")

post_template = jinja2.Template("""
<div class='cards'>
{% for card in cards %}
	<img src="{{ card.tumblr_url }}" alt="{{ card.name }}">
{% endfor %}
</div>

<p>{{ notes }}</p>
""")

client = pytumblr.TumblrRestClient(
  '5B0zCBEOD9NPFqr4U2D2uBhs9UfBbhYyTlNqDN7SWN9b85G0yv',
  'mnQTL22tBorL91nXAbQ7PK9m7A3ss8ddTgKNAFq7SBsKjMwIiE',
  'uf1pcaB3R83uuDEWpCbxhpIHc8UplA111F1Wlq6QkRkKyhSaXp',
  '1RDNpePi4Jptq4ImzstmPSDYUtxxMkRn0SK6EPmcg8tf3FIwdM'
)

class Proxy(object):
	def __init__(self, other):
		self.other = other

	def __getattr__(self, name):
		return getattr(self.other, name)


class TumblrUrlDecorator(Proxy):
	def __init__(self, urls, card):
		super(TumblrUrlDecorator, self).__init__(card)
		self.card = card
		self.urls = urls

	@property
	def tumblr_url(self):
		return self.urls.get_url(self.card.multiverseid)


def linkify(src):
	def card_link(name):
		card = db.get_card_sloppy(name)
		return '<a href="{0}">{1}</a>'.format(card.url, card.name)

	pattern = re.compile(r"\[([^\]]*)\]")
	return pattern.sub(lambda m: card_link(m.groups()[0]), src)

class TumblrUrls(object):
	def __init__(self, urls):
		self.urls = urls

	def decorate(self, card):
		return TumblrUrlDecorator(self, card)

	def get_url(self, multiverseid):
		sizes = self.urls.get(str(multiverseid), None)
		if sizes:
			for size in sizes:
				if size['width'] == 100:
					return size['url']

		raise Exeception("Missing URL:", multiverseid)

		

def main():
	with open('tumblred.json') as f:
		url_data = json.load(f)

	
	urls = TumblrUrls(url_data)

	pending = path('posts/pending')
	posted = path('posts/posted')
	for name in os.listdir(pending):
		
		with open(pending / name) as f:
			post = json.load(f)
		
		cards = [urls.decorate(db.get_card_by_id(id)) for id in post["cards"]]
		notes = linkify(post['notes'])
		body = post_template.render(cards = cards, notes = notes)

		print "Posting:", name
		client.create_text("packonepickone", state="queue", tags=["mtg", "p1p1"], body = body, format = "html")
		shutil.move(pending / name, posted / name)




if __name__ == "__main__":
	main()
