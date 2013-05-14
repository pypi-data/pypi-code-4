
################################################################################

from distutils.core import setup

from codecs import open

################################################################################

def read(fname):
	return open(fname, "r", "utf-8-sig").read()

################################################################################

setup (
	name = "jsoncomment",
	version = "0.1.0",
	description = "A wrapper to JSON parsers allowing comments and multi line strings",
	author = "Gaspare Iengo",
	author_email = "gaspareiengo@gmail.com",
	keywords = "json comments multiline",
	url = "https://bitbucket.org/Dando_Real_ITA/json-comment",
	packages = [
		"jsoncomment"
	],
	long_description = read("README.md"),
	classifiers = [
		"Development Status :: 3 - Alpha",
		"Intended Audience :: End Users/Desktop",
		"License :: OSI Approved :: MIT License",
		"Natural Language :: English",
		"Operating System :: OS Independent",
		"Programming Language :: Python",
		"Programming Language :: Python :: 3.3",
		"Topic :: Software Development :: Pre-processors",
		"Topic :: Text Editors :: Text Processing",
	],
)

################################################################################
