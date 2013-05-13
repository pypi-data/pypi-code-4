#!/usr/bin/env python
from distutils.core import setup

setup(
    name="django-query-exchange-fc",
    version="1.0",
    license="New BSD License",
    author='Alex Koshelev',
    author_email="daevaorn@gmail.com",
    url="http://github.com/futurecolors/django-query-exchange/",
    packages=[
        'query_exchange',
        'query_exchange.templatetags',
    ],
    description="Django application for handling GET query params for url creation",
    classifiers=[
        "Framework :: Django",
        "License :: OSI Approved :: BSD License",
    ]
)
