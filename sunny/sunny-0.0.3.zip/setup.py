from setuptools import setup
import os
import sys

if __name__ == '__main__':
    if sys.argv[-1] == 'publish':
        os.system('python setup.py sdist upload')
        sys.exit()

setup(
    name = "sunny",
    version = "0.0.3",
    author = "Deniz Dogan",
    author_email = "deniz@dogan.se",
    description = "Minimalistic interface to Solr.",
    license = "BSD",
    keywords = "solr search",
    url = "http://denizdogan.github.io/sunny/",
    packages=['sunny'],
    long_description=open('README.md').read(),
    install_requires=open('requirements.txt').readlines(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 2",
        "Topic :: Internet :: WWW/HTTP :: Indexing/Search",
    ],
)
