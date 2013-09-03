#!/usr/bin/env python

from setuptools import setup

setup(
    name='dotfigure',
    version='0.4',
    description='DOT graph figures for reStructuredText',
    long_description="""\
This package provides a docutils directive that integrates DOT graphs into the reST text.

reST example::

    .. dotfigure::

       digraph G {
           id1 -> id1;
           id2 -> id2;
           id1 -> id3;
           id2 -> id3;
           id3 -> id4;
       }

This directive requires a working Graphviz (http://www.graphviz.org) installation.

Please see README.txt for examples.
""",
    author='Friedrich Freitag',
    author_email='frauededed@gmx.net',
    py_modules=['dotfigure'],
    install_requires=['docutils'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: Public Domain',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Topic :: Documentation',
        'Topic :: Utilities',
    ],
    entry_points = {
        'docutils.parsers.rst.directives': [
            'dotfigure = dotfigure:DotFigureDirective'
        ],
    },
)
