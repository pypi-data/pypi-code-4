import os
from setuptools import setup, find_packages

def get_long_description():
    with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as f:
        return f.read()

setup(
    name = 'clplot',
    version = __import__('clplot').get_version(),
    url = 'https://github.com/breisfeld/clplot',
    author = 'Brad Reisfeld',
    author_email = 'brad.reisfeld@gmail.com',
    description = "clplot is a command line utility to create plots and pages of plots from csv-like files.",
    long_description = get_long_description(),
    keywords = 'plotting, matplotlib',
    install_requires = [],
    packages = find_packages(),
    include_package_data = True,
    entry_points={
        'console_scripts': [
            'clplot = clplot.main:main',
        ]},
    classifiers = [
        'Programming Language :: Python :: 2',
        'Development Status :: 3 - Alpha',
        'Operating System :: OS Independent',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Topic :: Utilities',
        'Topic :: Scientific/Engineering',
    ],
)
