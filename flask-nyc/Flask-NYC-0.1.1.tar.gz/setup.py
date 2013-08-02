from setuptools import setup

long_description = """
To install::

    pip install Flask-NYC

To use::

    from flask.ext import nyc
"""

setup(
    name='Flask-NYC',
    version='0.1.1',
    description='New York Flask Meetup',
    long_description=long_description,
    author='Andy Dirnberger',
    author_email='dirn@dirnonline.com',
    url='http://flask-nyc.org',
    py_modules=['flask_nyc'],
    install_requires=['flask>=0.8'],
)
