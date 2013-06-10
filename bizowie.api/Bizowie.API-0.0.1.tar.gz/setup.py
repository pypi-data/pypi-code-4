from distutils.core import setup

if __name__ == '__main__':
	import sys

	setup(
		name = 'Bizowie.API',
		version = '0.0.1',

		author = "Michael Flickinger",
		author_email = "mjflick@gnu.org",
		description = "A Python interface to the Bizowie API",
		keywords = "bizowie api",
		license = "Python",
		long_description = "This package implements an interface to the Bizowie API",
		platforms = 'any',
		packages = ['Bizowie'],
		url = "http://bizowie.com/api/",
		classifiers = [
			"Development Status :: 4 - Beta",
			"Intended Audience :: Developers",
			"Operating System :: OS Independent",
			"Programming Language :: Python",
			"Topic :: Software Development :: Libraries :: Python Modules",
		]
	)
