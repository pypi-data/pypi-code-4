# coding: utf-8

from distutils.core import setup

setup(
    name='xbcfg',
    version='0.2',
    author=u'Lauri Võsandi',
    author_email='lauri.vosandi@gmail.com',
    packages=['xbcfg'],
    scripts=['bin/xbcfg'],
    url='http://bitbucket.org/lauri.vosandi/xbcfg',
    zip_safe=False,
    license='LICENSE',
    description='Yet another X-CTU replacement',
    long_description=open('README.rst').read(),
    install_requires=[
        "crc16",
    ],
)
