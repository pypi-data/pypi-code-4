from setuptools import setup
import os

try:
    long_desc = open(os.path.join(os.path.dirname(__file__), 'README.md')).read()
except (IOError, OSError):
    long_desc = ''

setup(
    name = "palu",
    version = '0.1',
    url = 'http://github.com/marimore/palu',
    author = 'Alex Kritikos',
    author_email = 'alex@8bitb.us',
    description = 'Palu is a small spider, a forked of patu.',
    long_description = long_desc,
    entry_points = {
        'console_scripts': ['palu = palu:main']
    },
    install_requires = ['httplib2', 'lxml', 'cssselect', 'requests'],
    py_modules = ['palu'],
)
