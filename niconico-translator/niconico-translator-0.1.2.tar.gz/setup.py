# -*- coding: utf-8 -*-
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


def readme():
    try:
        with open('README.rst') as f:
            return f.read()
    except IOError:
        return


setup(
    name='niconico-translator',
    version='0.1.2',
    description='Translating comments on Nico Nico Douga (ニコニコ動画).',
    long_description=readme(),
    url='https://bitbucket.org/dahlia/niconico-translator',
    author='Hong Minhee',
    author_email='minhee' '@' 'dahlia.kr',
    license='AGPLv3',
    py_modules=['niconico_translator'],
    install_requires=[
        'dnspython3 >= 1.11.0',
        'html5lib >= 1.0b1',
        'lxml >= 3.2.0',
        'requests >= 1.2.0',
        'waitress >= 0.8',
        'WebOb >= 1.2.1'
    ],
    entry_points={
        'console_scripts': ['niconico-translator = niconico_translator:main']
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'Natural Language :: Japanese',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: Stackless',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content :: Message Boards',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
        'Topic :: Multimedia :: Sound/Audio :: Players',
    ]
)
