#!/usr/bin/env python
import os
from setuptools import setup, findall
from collections import defaultdict

def collect_files(path, prefix=''):
    ret = defaultdict(list)
    files = findall(path)
    for f in files:
        ret[os.path.join(prefix,os.path.dirname(f))].append(f)
    return ret.items()


setup(
    name='gap',
    version='0.2',
    description='Google App Engine project bootstrap',
    author='Robin Gottfried',
    author_email='google@kebet.cz',
    url='https://github.com/czervenka/gap',
    license='Apache License 2.0',
    packages=['gap', 'gap.utils'],
    scripts=['gap/bin/gap'],
    zip_safe = False,
    include_package_data=True,
    keywords='google appengine framework',
    requires=[],
)
