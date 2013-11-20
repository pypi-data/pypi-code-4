# -*- coding: utf-8 -*-
from setuptools import setup, find_packages, Extension

version = '0.1.1'


setup(name='languagedet',
    version=version,
    description="Python package for language detection.",
    long_description="""\
""",
    classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    keywords='',
    author='Karel Antonio Verdecia Ortiz',
    author_email='kverdecia@uci.cu',
    url='',
    license='LGPL3',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    package_data = {
        '': ['data/*.*'],
    },
    zip_safe=True,
    entry_points="""
    # -*- Entry points: -*-
    """,
    ext_modules=[
        Extension('languagedet._textcat', ['src/languagedet._textcat.c'],
            libraries=['exttextcat']),
    ],
)
