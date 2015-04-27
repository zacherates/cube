import codecs
import json
import pdb
import sys

def main():
	with open("AllSets.json") as f:
		sets = json.load(f)

	cards = {}
	for expansion in sets:
		for card in sets[expansion]['cards']:
			name = card['name']
			cards[name] = card

	print str(cards)[:256]

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
			print halves

			def fuse(name):
				return list(set(halves[0][name] + halves[1][name]))

			return {
				'name': name,
				'types': fuse('types'),
				'colors': fuse('colors')
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
	}

	wubrg = "WUBRGMCL"

	for name in lines():
		card = get_card(name)
		if card:
			get_section(card).append(card)
		else:
			raise NameError("Missing card: " + name)


	for section in wubrg:
		print section, len(sections[section])

	print "\n\n"


	for section in wubrg:
		print "{0} ({1})".format(section, len(sections[section]))
		print "--------"
		show(sections[section])
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

	with codecs.open("out/gallery.html", "w", 'utf-8') as html:
		render(gallery(sections), out = html)
		
def gallery_head():
	yield """<!DOCTYPE html>
		<html>
			<meta charset="utf-8">
			<link rel="stylesheet" href="../styles.css">
			<div class="gallery">
	"""

def gallery_foot():
	yield """
			</div>
		</html>
	"""


def gallery_section(section):
	cards = sorted(section, key = lambda card: card['name'])
	yield "\n".join(u'<img class="card" src="http://api.mtgdb.info/content/card_images/{0}.jpeg" alt="{1}">'.format(card.get('multiverseid'), card.get("name")) for card in cards)

def show(section, out = sys.stdout):
	cards = sorted(section, key = lambda card: card['name'])
	print >> out, "\n".join(card['name'] for card in cards)

def lines():
	with codecs.open("cards.txt", "r", "utf-8") as f:
		lines = f.readlines()

	return [line.strip() for line in lines]

if __name__ == "__main__":
	main()
