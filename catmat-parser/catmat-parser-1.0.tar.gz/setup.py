try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'A simple Catmat (SIASG) XML Parser',
    'author': 'Oswaldo Ferreira',
    'url': 'https://github.com/oswluiz/CatmatParser',
    'download_url': 'https://github.com/oswluiz/CatmatParser',
    'author_email': 'oswluizf@gmail.com',
    'version': '1.0',
    'install_request': ['should_dsl'],
    'packages': ['catmat'],
    'scripts': [],
    'name': 'catmat-parser'
}

setup(**config)
