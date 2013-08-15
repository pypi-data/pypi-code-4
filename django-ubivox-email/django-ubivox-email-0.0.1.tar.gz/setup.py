#!/usr/bin/env python

from distutils.core import setup

setup(
    name="django-ubivox-email",
    version="0.0.1",
    description="Django e-mail backend for the Ubivox e-mail API.",
    author="Christian Joergensen",
    author_email="christian.joergensen@ubivox.com",
    url="https://bitbucket.org/ubivox/django-ubivox-email",
    packages=["django_ubivox_email"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2 :: Only",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Framework :: Django",
    ],
    license="LGPLv3",
)
