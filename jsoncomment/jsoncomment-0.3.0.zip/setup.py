
################################################################################

from distutils.core import setup

################################################################################

def read(fname):
	return open(fname).read()

################################################################################

DESCRIPTION = """
A wrapper to JSON parsers allowing comments,
multiline strings and trailing commas
"""

################################################################################

setup (
	name = "jsoncomment",
	version = "0.3.0",
	description = DESCRIPTION,
	author = "Gaspare Iengo",
	author_email = "gaspareiengo@gmail.com",
	keywords = "json comments multiline",
	url = "https://bitbucket.org/Dando_Real_ITA/json-comment",

	package_dir = {
		'jsoncomment': 'src'
	},

	packages = [
		"jsoncomment",
		"jsoncomment.package",
	],

	package_data = {
		"jsoncomment": [
			"COPYING",
			"README.md",
			"README.rst",
			"doc/*.*",
			"examples/*.*",
		],
	},

	long_description = read("src/README.rst"),

	classifiers = [
		"Development Status :: 4 - Beta",
		"Intended Audience :: End Users/Desktop",
		"License :: OSI Approved :: MIT License",
		"Natural Language :: English",
		"Operating System :: OS Independent",
		"Programming Language :: Python",
		"Programming Language :: Python :: 2.7",
		"Programming Language :: Python :: 3.3",
		"Topic :: Software Development :: Pre-processors",
		"Topic :: Text Editors :: Text Processing",
	],
)

################################################################################
