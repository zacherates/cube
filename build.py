import codecs
import datetime
import json
import pdb
import re
import sys

from paver.easy import *

def main():
	with open("AllSets.json") as f:
		sets = json.load(f)

	cards = {}
	for expansion in sets:
		for card in sets[expansion]['cards']:
			if 'multiverseid' in card:
				name = card['name']
				cards[name] = card

	def get_section(card):
		if "Land" in card['types']:
			return sections['L']
		
		if 'colors' not in card or len(card['colors']) == 0:
			return sections['C']

		if len(card['colors']) == 1:
			color, = card['colors']
			return sections[abbreviations[color]]

		return sections['M']

	def get_card(name):
		if "//" in name:
			halves = [cards.get(part.strip()) for part in name.split("//")]

			def fuse(name):
				return list(set(halves[0][name] + halves[1][name]))

			return {
				'name': name,
				'types': fuse('types'),
				'colors': fuse('colors'),
				'cmc': halves[0]['cmc'] + halves[1]['cmc'],
				'multiverseid': halves[0]['multiverseid']
			}

		return cards.get(name)

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

	abbreviations = {
		"White": "W",
		"Blue": "U",
		"Black": "B",
		"Red": "R",
		"Green": "G",
		"Land": "L",
		"Colourless": "C",
		"Multi-colour": "M",
	}

	abbreviations_reverse = dict((v, k) for (k, v) in abbreviations.items())

	def stat(name):
		def counter(cards):
			return sum(1 for card in cards if name in card['types'])
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
		card = get_card(name)
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

	def render(template, out = sys.stdout):
		if isinstance(template, basestring):
			out.write(template)
		else:
			for part in template:
				render(part, out = out)

	def gallery(sections):
		yield gallery_head()
		for section in wubrg:
			yield gallery_section(sections[section])
		yield gallery_foot()

	def histogram(samples):
		results = [0] * 10
		for sample in samples:
			index = sample if sample < len(results) else -1
			results[index] += 1
		return results[1:]

	def curve(cards):
		return histogram(card.get('cmc', 0) for card in cards)

	def power(cards):
		return histogram(int(card.get('power', 0)) for card in cards)

	def creature_curve(cards):
		return curve(card for card in cards if 'Creature' in card.get('types', []))

	def stats(sections):
		yield '<script src="../media/jquery-2.1.4.js"></script>'
		yield '<script src="../media/jquery.sparkline-2.1.2.js"></script>'
		yield '<link rel="stylesheet" href="../media/styles.css">'
		yield "<table id='stats'>"
		yield "<tr><th>Color</th><th>Creatures</th><th>Instants</th><th>Sorceries</th><th>Enchantments</th><th>Total</th><th>Curve</th><th>(Creatures)</th></tr>"
		for section in wubrg:
			cards = sections[section]
			name = abbreviations_reverse[section]
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


def gallery_section(section):
	cards = sorted(section, key = lambda card: card['name'])
        tmpl = u'''<a href="http://gatherer.wizards.com/Pages/Card/Details.aspx?multiverseid={0}" class="card {2}">
            <img src="http://gatherer.wizards.com/Handlers/Image.ashx?multiverseid={0}&type=card" alt="{1}">
        </a>''' 

        def colors(card):
            colors = card.get('colors')
            if not colors or len(colors) < 1:
                return "colorless"

            if len(colors) > 1:
                return "multi"

            return colors[0]


        def types(card):
            return u' '.join(card.get('types', []) + [colors(card)]).lower()

	yield "\n".join(tmpl.format(card.get('multiverseid'), card.get("name"), types(card)) for card in cards)

def show(section, out = sys.stdout):
	cards = sorted(section, key = lambda card: card['name'])
	print >> out, "\n".join(card['name'] for card in cards)

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


if __name__ == "__main__":
	main()
