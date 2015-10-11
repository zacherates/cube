import codecs
import csv
import datetime
import difflib
import json
import logging
import pdb
import re
import sys

from paver.easy import *

from card_db import CardDB, Card


def main():
	db = CardDB.default()

	def get_section(card):
		if card.is_land():
			return sections['L']
		
		if len(card.colors) == 0:
			return sections['C']

		if len(card.colors) == 1:
			color = card.colors[0]
			return sections[db.abbreviations[color]]

		return sections['M']

	sections = {
		"W": [],			
		"U": [],			
		"B": [],			
		"R": [],			
		"G": [],			
		"M": [],			
		"C": [],			
		"L": [],			
	}


	def stat(name):
		def counter(cards):
			return sum(1 for card in cards if name in card.types)
		return counter

	creatures = stat("Creature")
	instants = stat("Instant")
	sorceries = stat("Sorcery")
	enchantment = stat("Enchantment")

	wubrg = "WUBRGMCL"

	for name in lines():
		match = re.match(r"^\s*([^#]*)\s*(?:#(\w+)\s*)*$", name)
		name, tags = match.groups()
		name = name.strip()
		card = db.get_card(name)
		if card:
			get_section(card).append(card)
		else:
			raise NameError("Missing card: '{0}'".format(name))


	for section in wubrg:
		print section, len(sections[section])

	print "\n\n"


	for section in wubrg:
		cards = sections[section]
		print "{0} ({1}, {2})".format(section, len(cards), creatures(cards))
		print "--------"
		show(cards)
		print "\n"

	def gallery(sections):
		yield gallery_head()
		for section in wubrg:
			by_name = sorted(sections[section], key = lambda card: card.name)
			yield gallery_section(by_name)
		yield gallery_foot()

	def histogram(samples):
		results = [0] * 10
		for sample in samples:
			index = sample if sample < len(results) else -1
			results[index] += 1
		return results[1:]

	def curve(cards):
		return histogram(card.cmc for card in cards)

	def power(cards):
		def get_power(card):
			try:
				return int(card.get('power', 0))
			except:
				return 0
		
		return histogram(get_power(card) for card in cards)

	def creature_curve(cards):
		return curve(card for card in cards if 'Creature' in card.types)

	def stats(sections):
		yield '<script src="../media/jquery-2.1.4.js"></script>'
		yield '<script src="../media/jquery.sparkline-2.1.2.js"></script>'
		yield '<link rel="stylesheet" href="../media/styles.css">'
		yield "<table id='stats'>"
		yield "<tr><th>Color</th><th>Creatures</th><th>Instants</th><th>Sorceries</th><th>Enchantments</th><th>Total</th><th>Curve</th><th>(Creatures)</th></tr>"
		for section in wubrg:
			cards = sections[section]
			name = db.abbreviations_reverse[section]
			yield '''<tr><td>{0}</td><td>{1}</td><td>{2}</td><td>{3}</td><td>{4}</td><td>{5}</td>
				<td><span class="inlinesparkline">{6}</span></td>
				<td><span class="inlinesparkline">{7}</span></td>
				<td><span class="inlinesparkline">{8}</span></td>
			</tr>
			'''.format(name, 
					creatures(cards), 
					instants(cards), 
					sorceries(cards), 
					enchantment(cards), 
					len(cards), 
					",".join(str(card) for card in curve(cards)), 
					",".join(str(card) for card in creature_curve(cards)),
					",".join(str(card) for card in power(cards)))
		yield "</table>"
		yield '<script src="../media/stats.js"></script>'

	with codecs.open("out/index.html", "w", 'utf-8') as html:
		render(gallery(sections), out = html)

	with codecs.open("out/stats.html", "w", 'utf-8') as stats_html:
		render(stats(sections), out = stats_html)

	package()
		
def gallery_head():
	yield """<!DOCTYPE html>
		<html>
			<meta charset="utf-8">
                        <title>Aaron's Peasant Cube</title>
                        <script src="media/jquery-2.1.4.js"></script>
                        <script src="media/cube.js"></script>

			<link rel="stylesheet" href="media/styles.css">

                        <div class="header">
                            <ul>
                                <li><a class="selected" id="all" href="javascript:void(0)">All</a></li>
                                <li><a id="creature" data-type="type" href="javascript:void(0)">Creatures</a></li>
                                <li><a id="instant" data-type="type" href="javascript:void(0)">Instants</a></li>
                                <li><a id="sorcery" data-type="type" href="javascript:void(0)">Sorceries</a></li>
                                <li><a id="enchantment" data-type="type" href="javascript:void(0)">Enchantments</a></li>
                                <li><a id="artifact" data-type="type" href="javascript:void(0)">Artifacts</a></li>
                                <li><a id="land" data-type="type" href="javascript:void(0)">Lands</a></li>
                                <li><a id="white" data-type="color" href="javascript:void(0)">White</a></li>
                                <li><a id="blue" data-type="color" href="javascript:void(0)">Blue</a></li>
                                <li><a id="black" data-type="color" href="javascript:void(0)">Black</a></li>
                                <li><a id="red" data-type="color" href="javascript:void(0)">Red</a></li>
                                <li><a id="green" data-type="color" href="javascript:void(0)">Green</a></li>
                                <li><a id="multi" data-type="color" href="javascript:void(0)">Multi</a></li>
                                <li><a id="colorless" data-type="color" href="javascript:void(0)">Colorless</a></li>
                            </ul>
                        </div>
                        <div id="gallery">
                            <div id="color-filter" class="filter">
                            <div id="type-filter" class="filter">
	"""

def gallery_foot():
	yield """
                            </div>
                            </div>
			</div>
		</html>
	"""


def gallery_section(cards, extra = lambda card: ''):
        tmpl = u'''<a href="http://gatherer.wizards.com/Pages/Card/Details.aspx?multiverseid={0}" class="card {2}">
            <img src="http://gatherer.wizards.com/Handlers/Image.ashx?multiverseid={0}&type=card" alt="{1}" title="{3}">
        </a>''' 

        def colors(card):
            colors = card.colors
            if not colors or len(colors) < 1:
                return "colorless"

            if len(colors) > 1:
                return "multi"

            return colors[0]


        def types(card):
            return u' '.join(card.types + [colors(card)]).lower()

	yield "\n".join(tmpl.format(card.multiverseid, card.name, types(card), extra(card)) for card in cards)


def render(template, out = sys.stdout):
	if isinstance(template, basestring):
		out.write(template)
	else:
		for part in template:
			render(part, out = out)


def show(section, out = sys.stdout):
	cards = sorted(section, key = lambda card: card.name)
	print >> out, "\n".join(card.name for card in cards)

def lines():
	with codecs.open("cards.txt", "r", "utf-8") as f:
		lines = f.readlines()

	return [line.strip() for line in lines]

def package():
    ID = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    target = path("dist") / "cube_{0}".format(ID)
    sh("mkdir -p " + target)
    sh("cp -r media out/index.html " + target)
    sh("cd dist && tar -czvf {0}.tar.gz {0}".format(target.name))

def set_review(path):
	def include_ratings(card):
		ratings = card.extra[2], card.extra[3]
		return 'mine: {0}, lsv: {1}'.format(*ratings)

	def load_card(rating):
		card = db.get_card_sloppy(rating[1])
		card.extra = rating
		return card

	db = CardDB.from_path("cards.json")
	with open(path) as f:
		ratings = list(csv.reader(f))[1:]
		
	cards = [load_card(rating) for rating in ratings]

	with codecs.open("out/ori.html", "w", 'utf-8') as html:
		render(gallery_section(cards, extra = include_ratings), out = html)

def dispatch(args):
	if len(args) == 0:
		main()
		return

	cmd = args.pop(0)
	if cmd == "review":
		set_review(*args)
	else:
		raise Exception("Unknown command '{0}'.".format(cmd))

if __name__ == "__main__":
	dispatch(sys.argv[1:])
