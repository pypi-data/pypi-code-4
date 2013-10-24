# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open('README.txt') as file:
    #long_description = file.read()
    readlines = file.readlines()
    long_description = "\n".join(readlines)

print long_description
setup(
    name = "torweb",
    version = "0.0.3",
    #packages = find_packages(exclude=["test.*", "test"]),
    packages = ["torweb"],
    include_package_data = True,
    author = "zhangpeng",
    author_email = "zhangpeng1@infohold.com.cn",
    url = "",
    description = "torweb",
    long_description=long_description,
    install_requires=[],
)
