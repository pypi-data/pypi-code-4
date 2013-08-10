#!/usr/bin/env python

from distutils.core import setup
from setuptools import find_packages

README_FILE = open('README.txt')
try:
    long_description = README_FILE.read()
finally:
    README_FILE.close()

exclude = [
        'nano.link',
        'nano.menu',
        'nano.menu.templatetags',
        'nano.timeline',
        'nano.tracker',
        'nano.uri',
        'nano.web20',
        'nano.web20.templatetags',
        'nano.yubiauth',
]

packages=(
        'nano',
        'nano.activation', 
        'nano.badge', 
        'nano.blog',
        'nano.comments',
        'nano.chunk',
        'nano.faq',
        'nano.mark',
        'nano.privmsg',
        'nano.tools',
        'nano.user',
)

setup(name='nano',
        version='0.5',
        packages=find_packages(exclude=exclude),
        include_package_data=True,
        zip_safe=False,
        platforms=['any'],
        description='Does less! Loosely coupled mini-apps for django.',
        author_email='kaleissin@gmail.com',
        author='kaleissin',
        long_description=long_description,
        url='http://code.google.com/p/django-nano/',
        classifiers=[
                'Development Status :: 4 - Beta',
                'Environment :: Web Environment',
                'Framework :: Django',
                'Intended Audience :: Developers',
                'License :: OSI Approved :: MIT License',
                'Operating System :: OS Independent',
                'Programming Language :: Python',
                'Topic :: Software Development :: Libraries :: Application Frameworks',
                'Topic :: Software Development :: Libraries :: Python Modules',
        ]
)
