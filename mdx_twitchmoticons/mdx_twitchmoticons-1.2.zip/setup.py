#!/usr/bin/env python
from setuptools import setup

setup(
    name='mdx_twitchmoticons',
    version='1.2',
    author='Andrew Horn',
    author_email='andrewphorn@gmail.com',
    description='Python-Markdown extension to support Twitch.tv-style emoticons.',
    url='https://github.com/andrewphorn/markdown.twitchmoticons',
    py_modules=['mdx_twitchmoticons'],
    install_requires=['Markdown>=2.0',],
    classifiers=[
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'Environment :: Web Environment',
        'Programming Language :: Python',
        'Topic :: Text Processing :: Filters',
        'Topic :: Text Processing :: Markup :: HTML'
    ]
)