try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import packer
Packer = packer.Packer


setup(
	name = Packer.name,
    version = Packer.version,
	description = 'A new type of package manager',
	long_description = open('README.rst').read(),
	url = 'http://github.com/kalail/packer',
	author = 'Kashif Malik',
	author_email = 'kashif@kalail.com',
	license=open('LICENSE').read(),
	packages = [
		'packer'
	],
	install_requires=[
		'requests',
	],
	zip_safe = False
)