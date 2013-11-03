# -*- coding: utf-8 -*-
# vim:fenc=utf-8


from setuptools import setup


with open("README.rst") as f:
    description = f.read()

setup(
    version="1.0.6",
    name="confiskus",
    description="INI style files parser with basic inheritance feature.",
    long_description=description,
    author="Michal Kuffa",
    author_email="michal.kuffa@gmail.com",
    py_modules=["confiskus"],
    license="BSD",
    url="https://github.com/beezz/confiskus",
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Topic :: Software Development",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
    ]
)
