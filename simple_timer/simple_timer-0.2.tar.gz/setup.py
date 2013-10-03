import os
from setuptools import setup, find_packages

try:
    readme = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()
except:
    readme = ''

version = '0.2'

setup(
    name = 'simple_timer',
    version = version,
    description = ("A timer module. Makes it easy to track elapsed time."),
    long_description = readme,
    classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
    ],
    keywords = 'timer',
    author = 'Artur Barseghyan',
    author_email = 'artur.barseghyan@gmail.com',
    url = 'https://bitbucket.org/barseghyanartur/timer',
    package_dir = {'':'src'},
    packages = find_packages(where='./src'),
    license = 'GPL 2.0/LGPL 2.1',
)
