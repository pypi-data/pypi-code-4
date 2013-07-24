# -*- coding: utf-8 -*

from setuptools import setup

setup(
    name="apirator",
    version="0.1.0",
    packages=["apirator"],
    install_requires=[
        "Django>=1.4",
    ],
    author="Victor Kotseruba",
    author_email="barbuzaster@gmail.com",
    url="https://github.com/barbuza/apirator",
    description="easily add simple http api to your django web app",
    license="MIT",
    keywords="django",
    zip_safe=True
)
