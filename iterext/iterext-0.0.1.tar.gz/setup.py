import os
from setuptools import find_packages, setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="iterext",
    version="0.0.1",
    url='http://github.com/aguil/iterext',
    author="Jason Aguilon",
    author_email="jaguilon@gmail.com",
    description='iterext: Python itertools recipes.',
    long_description=read('README.rst'),
    packages=find_packages(),
    classifiers=['Development Status :: 5 - Production/Stable',
                 'Intended Audience :: Developers',
                 'License :: OSI Approved :: MIT License',
                 'Natural Language :: English',
                 'Programming Language :: Python :: 2',
                 'Programming Language :: Python :: 2.7',
                 'Topic :: Software Development :: Libraries',
                 'Topic :: Utilities'])
