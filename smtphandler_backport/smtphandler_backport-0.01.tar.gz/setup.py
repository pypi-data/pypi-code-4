import os
from setuptools import setup

dependencies = []

setup(
    name = "smtphandler_backport",
    version = "0.01",
    author = "Ulas Tuerkmen",
    author_email = "ulas.tuerkmen@gmail.com",
    description = ("Backport to Python 2.6 of the SMTPHandler in higher versions."),
    install_requires = [],
    test_suite = 'nose.collector',
    tests_require = ['mock', 'nose'],
    packages=['smtphandler_backport'],
    url = "https://github.com/afroisalreadyinu/smtphandler_backport",
)
