try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup

setup(
    name = "espn_py",
    version = "0.1",
    url='https://github.com/talam/espn-py',
    license = "MIT",
    author = "Tanvir Alam",
    packages = find_packages(),
    install_requires = ['requests>=1.2.3'],
    author_email = "tanviralam2@gmail.com",
    description = "Simple python wrapper around the ESPN API",
    keywords = "ESPN API Wrapper",
)