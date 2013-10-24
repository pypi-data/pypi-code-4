# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


setup(
    name = "torweb",
    version = "0.0.1",
    #packages = find_packages(exclude=["test.*", "test"]),
    packages = ["torweb"],
    include_package_data = True,
    author = "zhangpeng",
    author_email = "zhangpeng1@infohold.com.cn",
    url = "http://182.48.115.36:20050",
    description = "torweb",
    install_requires=[],
)
