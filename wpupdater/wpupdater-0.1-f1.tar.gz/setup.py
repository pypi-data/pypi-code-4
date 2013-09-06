try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'WordPress Updater',
    'author': 'Marcin Matlaszek <emate>, inFakt DevTeam',
    'url': 'http://github.com/infakt/wpupdater',
    'download_url': 'http://github.com/infakt/wpupdater',
    'author_email': 'mmatlaszek@gmail.com, marcin.matlaszek@infakt.pl, devteam@infakt.pl',
    'version': '0.1-f1',
    'install_requires': ['lxml'],
    'packages': ['wpupdater'],
    'scripts': ['bin/wpupdate.py'],
    'name': 'wpupdater'
}

setup(**config)
