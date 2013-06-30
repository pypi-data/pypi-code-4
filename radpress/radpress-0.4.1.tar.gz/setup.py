# -*- coding: utf-8 -*-
import os
from setuptools import setup, find_packages

pkg_name = 'radpress'
version = __import__(pkg_name).__version__

PROJECT_DIR = os.path.dirname(__file__)

# get requires from requirements/global.txt file.
requires_file_name = os.path.join(PROJECT_DIR, 'requirements', 'global.txt')
with file(requires_file_name) as install_requires:
    install_requires = map(lambda x: x.strip(), install_requires.readlines())

try:
    import importlib

except ImportError:
    install_requires.append('importlib')

setup(
    name=pkg_name,
    version=version,
    description='Simple reusable blog application',
    long_description=file(os.path.join(PROJECT_DIR, 'README.rst')).read(),
    author=u'Gökmen Görgen',
    author_email='gokmen@radity.com',
    license='MIT',
    url='https://github.com/gkmngrgn/radpress',
    packages=find_packages(exclude=['venv', 'demo', 'docs']),
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Framework :: Django",
        "Environment :: Web Environment"
    ]
)
