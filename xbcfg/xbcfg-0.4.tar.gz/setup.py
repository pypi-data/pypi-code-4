# coding: utf-8

import os
import codecs
from distutils.core import setup

README =  codecs.open(
    os.path.join(os.path.dirname(__file__), "README.rst"),
    encoding="utf-8" ).read()

setup(
    name='xbcfg',
    version='0.4',
    author=u'Lauri Võsandi',
    author_email='lauri.vosandi@gmail.com',
    packages=['xbcfg'],
    scripts=['bin/xbcfg'],
    url='http://bitbucket.org/lauri.vosandi/xbcfg',
    license='LICENSE',
    description='Yet another X-CTU replacement',
    long_description=README,
    install_requires=[
        "crc16",
    ],
)
