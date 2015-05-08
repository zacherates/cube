import datetime
import glob
import os, os.path
import re

from fabric.api import *

@hosts("maenpaa.ca")
def deploy():
	path = sorted(glob.glob("dist/cube_*.tar.gz"))[-1]
	_, name = os.path.split(path)
	id, = re.search(r"(\d+)", name).groups(0)
	

	put(path)
	run("mv ~/{0} ~/cube".format(name))
	with cd("~/cube"):
		run("tar -xzvf " + name)

	with cd("~/public_html"):
		run("ln -s ~/cube/cube_{0} tmp-{0} && mv -T tmp-{0} cube".format(id))
