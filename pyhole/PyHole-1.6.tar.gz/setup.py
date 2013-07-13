# from distutils.core import setup
from setuptools import setup

setup(
    name='PyHole',
    version='1.6',
    author="Krzysztof Dorosz",
    author_email="cypreess@gmail.com",
    description=("Simple generic REST API client."),
    license="LGPL",
    keywords="REST api connect connector client pyhole",
    packages=['pyhole', 'test'],
    long_description=open('README.rst').read(),
    url="http://packages.python.org/pyhole",
    classifiers=[
        "Topic :: Utilities",
        "Topic :: Internet :: WWW/HTTP",
        "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",

    ],
    requires=['pyyaml', ],

 )
