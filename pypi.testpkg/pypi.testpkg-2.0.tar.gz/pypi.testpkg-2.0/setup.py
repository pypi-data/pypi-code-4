#from distutils.core import setup
from setuptools import setup

setup(
    name="pypi.testpkg",
    version="2.0",
    packages=["testpkg"],
    install_requires=["requests"],
)
