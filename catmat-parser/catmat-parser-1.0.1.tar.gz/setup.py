try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'A simple Catmat (SIASG) XML Service',
    'author': 'Oswaldo Ferreira',
    'url': 'https://github.com/oswluiz/CatmatParser',
    'download_url': 'https://github.com/oswluiz/CatmatParser',
    'author_email': 'oswluizf@gmail.com',
    'version': '1.0.1',
    'install_requires': ['should_dsl', 'requests'],
    'packages': ['catmat'],
    'scripts': [],
    'name': 'catmat-parser'
}

setup(**config)
