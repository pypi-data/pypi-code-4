# -*- coding: utf-8 -*-

import os

from setuptools import setup


README = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name = "django-hitcounter",
    version = "0.1.1",
    url = 'https://github.com/TracyWebTech/django-hitcounter',
    license = 'BSD License',
    description = "Django hitcounter tracks the number of hits/views for chosen objects",

    author = 'Tracy Web Technologies',
    author_email = 'contato@tracy.com.br',

    packages = ['hitcounter', ],
    include_package_data=True,

    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Plugins',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
