#!/usr/bin/env python
from setuptools import setup, find_packages
setup(
        name = "classgraph",
        version = "0.1",
        packages = find_packages(),
        scripts = ['classgraph.py'],
        author = "Panagiotis H.M. Issaris",
        author_email = "takis@issaris.org",
        description = "Generate a Graphviz diagram of Python classes",
        long_description = """
This script generates a Graphviz .dot file containing a diagram of the class
hierarchies.""",
        license = "GPL",
        url = "http://www.issaris.org/",
        platforms=["linux"],
        classifiers = [
            'Environment :: Console',
            ],
        )
