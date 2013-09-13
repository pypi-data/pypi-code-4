# Matthew Henderson, 2012
# Created: Wed Aug  8 15:37:51 BST 2012.
# Last updated: Mon Apr 15 20:17:58 BST 2013.

from setuptools import setup

def readme():
    with open('README.md') as f:
        return f.read()

setup(
    name = 'ryser',
    version = '0.0.8',
    packages = ['ryser',],
    description = "Latin Squares and Related Designs.",
    author = "Matthew Henderson",
    author_email = "matthew.james.henderson@gmail.com",
    scripts = ['bin/counterexample_investigation.py',
               'bin/hiltons_claim.py'],
    url = "http://packages.python.org/ryser/",
    download_url = "http://pypi.python.org/pypi/ryser/",
    keywords = [""],
    classifiers = [
        "Programming Language :: Python",
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
    license = 'LICENSE.txt',
    long_description = readme(),
    install_requires=[
        "networkx >= 1.7.0",
        "vizing >= 0.0.11",
    ],
)

