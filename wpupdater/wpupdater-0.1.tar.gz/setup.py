try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'WordPress Updater',
    'author': 'Marcin Matlaszek, inFakt DevTeam',
    'url': 'github.com/infakt/wpupdater',
    'download_url': 'github.com/infakt/wpupdater',
    'author_email': 'marcin.matlaszek@infakt.pl, devteam@infakt.pl',
    'version': '0.1',
    'install_requires': ['lxml'],
    'packages': ['wpupdater'],
    'scripts': ['bin/wpupdate.py'],
    'name': 'wpupdater'
}

setup(**config)
