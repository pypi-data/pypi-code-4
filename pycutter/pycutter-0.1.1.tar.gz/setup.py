#-*- coding:utf-8 -*-
"""
pycutter
~~~~~~

pycutter is a simple screen shot tool in Python.
"""

from setuptools import setup

install_requires = []

entry_points = """
[console_scripts]
pycutter = pycutter:start_window
"""

setup(
    name = 'pycutter',
    version = '0.1.1',
    description = 'A simple screen shot tool',
    long_description = __doc__,
    author = 'DanielBlack',
    author_email = 'danielblack@danielblack.name',
    license = "MIT",
    url = 'http://github.com/DanielBlack/pycutter',
    packages = ['pycutter'],
    scripts = ['scripts/pycutter'],
    entry_points=entry_points,
    install_requires=install_requires,
    classifiers = [
        "Development Status :: 3 - Alpha",
        "Environment :: X11 Applications :: Qt",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        ],
    zip_safe=False,
)
