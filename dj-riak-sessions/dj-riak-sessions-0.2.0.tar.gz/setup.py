import os
from setuptools import setup
from riak_sessions import __version__

def read(filename):
    return open(os.path.join(os.path.dirname(__file__), filename)).read()

packages = ['riak_sessions']

setup(
    name='dj-riak-sessions',
    version=__version__,
    description="Django session backend that stores sessions in a Riak database",
    long_description=read("README.md"),
    keywords='django, sessions, riak',
    author="Ales Bublik",
    author_email="ales.bublik@gmail.com",
    url='http://github.com/alesbublik/dj-riak-sessions',
    license='BSD',
    packages=packages,
    zip_safe=False,
    install_requires=['riak>=1.5.0'],
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Framework :: Django",
        "Environment :: Web Environment",
        ],
)
