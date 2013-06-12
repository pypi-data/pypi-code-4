#!/usr/bin/env python

from distutils.core import setup
from signup import __version__

setup(
	name='django-signup',
	version=__version__,
	description='A user registration app for Django with support for custom user models',
	author='Felipe Bessa Coelho',
	author_email='fcoelho.9@gmail.com',
	url='http://bitbucket.org/fcoelho/django-signup/',
	packages=['signup'],
)
