#!/usr/bin/env python
# coding=utf-8
"""
Graf

A light weight numpy, scipy, and matplotlib wrapper library.

graf can be used as a module for your python code or write graf script
and run with graf program.
The following code is an example of graf script.

    #!/usr/bin/env graf

    # load data from filesystem
    x, y = load('gallery/raw/data1.txt', using=(0, 1))

    # plot xy data
    plot(x, y)

    # draw xlabel, ylabel, or so on
    title('A graf example')
    xlabel('Wavelength [nm]')
    ylabel('Intensity')
    grid()

    # save to a PNG file
    savefig('example.png')

    # save to a SVG file
    savefig('example.svg')

    # show interactive graph window
    show()

graf also can be extended with plugins. See documentation for instraction or
development.

(C) 2013 hashnote.net, Alisue
"""
name = 'graf'
version = '0.1.1'
author = 'Alisue'
author_email = 'lambdalisue@hashnote.net'

import os
from setuptools import setup, find_packages

def read(filename):
    filename = os.path.join(os.path.dirname(__file__), filename)
    if os.path.exists(filename):
        return open(os.path.join(os.path.dirname(__file__), filename)).read()
    return __doc__

setup(
    name=name,
    version=version,
    description = "Light weight numpy, scipy, and matplotlib wrapper",
    long_description=read('README.txt'),
    classifiers = [
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
    ],
    keywords = "numpy, scipy, matplotlib, gnuplot, plot, graph, analysis",
    author = "Alisue",
    author_email = "lambdalisue@hashnote.net",
    url=r"https://github.com/lambdalisue/graf",
    download_url = r"https://github.com/lambdalisue/graf/tarball/master",
    license = 'MIT',
    packages = find_packages('src'),
    package_dir = {'': 'src'},
    include_package_data = True,
    exclude_package_data = {'': ['README.txt']},
    zip_safe = True,
    install_requires=[
        'setuptools',
        'PyYAML',
        'natsort',
    ],
    entry_points={
        'console_scripts': [
            'graf = graf.console:main',
        ],
        'graf.plugins': [
            'load = graf.builtins.load:__plugin__',
            'pyplot = graf.builtins.pyplot:__plugin__',
            'styles.color_cycle = graf.builtins.styles:color_cycle',
            'styles.linestyle_cycle = graf.builtins.styles:linestyle_cycle',
            'styles.markerstyle_cycle = graf.builtins.styles:markerstyle_cycle',
            'loaders.PlainLoader = graf.plugins.loaders.plain:PlainLoader',
            'parsers.PlainParser = graf.plugins.parsers.plain:PlainParser',
            'filters.sma = graf.plugins.filters.sma:__plugin__',
            'filters.relative = graf.plugins.filters.relative:__plugin__',
            'filters.statistics = graf.plugins.filters.statistics:__plugin__',
        ],
    },
)

