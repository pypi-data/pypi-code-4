try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'Great wrapper for bit.ly',
    'author': 'Marcin Lipiec',
    'url': 'http://pypi.python.org/pypi/PyBitly/',
    'author_email': 'marcin.lipiec@yamatai.pl',
    'version': '0.1.1',
    'install_requires': ['simplejson'],
    'packages': ['pybitly', 'pybitly.test'],
    'name': 'PyBitly',
    'license': 'GNU GENERAL PUBLIC LICENSE Version 3',
    'long_description': open('README.txt').read(),
}

setup(**config)