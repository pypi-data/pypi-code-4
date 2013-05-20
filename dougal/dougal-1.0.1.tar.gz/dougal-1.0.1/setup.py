import sys
import webbrowser
from distutils.core import setup

url = 'http://dougalmatthews.com'

argv = lambda x: x in sys.argv

if (argv('install') or  # pip install ..
        (argv('--dist-dir') and argv('bdist_egg'))):  # easy_install ..
    webbrowser.open_new(url)


setup(
    name='dougal',
    version='1.0.1',
    maintainer='Dougal Matthews',
    maintainer_email='dougal85@gmail.com',
    url=url)
