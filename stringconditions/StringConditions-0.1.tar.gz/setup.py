from setuptools import setup

readme = open( 'README.md' ).read()

setup(
	name = 'StringConditions',
	version = '0.1',
	author = 'Mihalcea Romeo',
	author_email = 'romeo.mihalcea@gmail.com',
	license = 'MIT',
	url = "https://github.com/ciokan/string_condition",
	description = 'A small python package which evaluates string based conditions',
	long_description = readme,
	py_modules = ['base']
)
