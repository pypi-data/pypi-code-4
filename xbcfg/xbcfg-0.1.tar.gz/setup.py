# coding: utf-8

from distutils.core import setup

setup(
    name='xbcfg',
    version='0.1',
    author=u'Lauri Võsandi',
    author_email='lauri.vosandi@gmail.com',
    packages=['xbcfg'],
    scripts=['bin/xbcfg'],
    url='http://bitbucket.org/lauri.vosandi/xbcfg',
    license='LICENSE',
    description='Yet another X-CTU replacement',
    long_description=open('README.rst').read(),
    install_requires=[
        "crc16",
    ],
)
