try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'webassets livescript filter',
    'author': 'Jorge Barata Gonzalez',
    'url': 'http://github.com/jorgebg/webassets-livescript',
    'download_url': 'http://github.com/jorgebg/webassets-livescript',
    'author_email': 'jorgebg',
    'version': '0.1',
    'install_requires': ['webassets'],
    'packages': ['webassets_livescript'],
    'scripts': [],
    'name': 'webassets-livescript',
    'license': 'MIT'
}

setup(**config)