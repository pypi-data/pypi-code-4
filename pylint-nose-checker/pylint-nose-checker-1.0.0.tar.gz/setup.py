from setuptools import setup

setup(
    name="pylint-nose-checker",
    version="1.0.0",
    url='http://github.com/OddBloke/pylint-nose-checker',
    license='GPLv3',
    description="A pylint plugin which fixes nose.tools import errors",
    author='Daniel Watkins',
    author_email='daniel@daniel-watkins.co.uk',
    py_modules=['nose_checker'],
    install_requires=['pylint', 'nose', 'logilab-astng'],
)
