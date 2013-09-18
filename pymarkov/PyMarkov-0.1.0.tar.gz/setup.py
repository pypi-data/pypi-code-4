try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name="PyMarkov",
    version="0.1.0",
    author="Slater Victoroff",
    author_email="Slater.R.Victoroff@gmail.com",
    packages=["pymarkov"],
    url="http://pypi.python.org/pypi/PyMarkov/",
    license="LICENSE.txt",
    description="Markov Chains made easy",
    long_description=open("README.txt").read(),
    install_requires=[],
)