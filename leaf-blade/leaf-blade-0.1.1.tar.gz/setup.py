from distutils.core import setup, Extension

long_description="""
A Python port of `Razor Leaf`__.

__ https://github.com/charmander/razorleaf
"""

escape = Extension("leafblade_escape", sources=["leafblade/escape.c"])

setup(
	name="leaf-blade",
	version="0.1.1",
	packages=["leafblade"],
	ext_modules=[escape],
	description="A template engine for HTML",
	long_description=long_description,
	url="https://github.com/charmander/leaf-blade",
	author="Charmander",
	author_email="campersander@gmail.com",
	classifiers=[
		"Programming Language :: Python :: 3",
		"Topic :: Internet :: WWW/HTTP :: Dynamic Content",
		"Topic :: Text Processing :: Markup :: HTML",
		"Development Status :: 2 - Pre-Alpha"
	]
)
