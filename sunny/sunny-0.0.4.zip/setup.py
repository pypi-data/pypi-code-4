from setuptools import setup
import os
import sys

if __name__ == '__main__':
    if sys.argv[-1] == 'publish':
        os.system('python setup.py sdist upload')
        sys.exit()

requirements = []
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

description = ''
with open('README.md') as f:
    description = f.read()

setup(
    name = "sunny",
    version = "0.0.4",
    author = "Deniz Dogan",
    author_email = "deniz@dogan.se",
    description = "Minimalistic interface to Solr.",
    license = "BSD",
    keywords = "solr search",
    url = "http://sunny.dogan.se/",
    packages=['sunny'],
    long_description=description,
    install_requires=requirements,
    extras_require = {
        'omdict':  ['orderedmultidict'],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 2",
        "Topic :: Internet :: WWW/HTTP :: Indexing/Search",
    ],
)
