from setuptools import setup, find_packages
import os, sys

install_requires = [
    "setuptools",
    'pymongo',
    'pytest',
    'zope.interface'
]

py_version = sys.version_info[:2]
PY3 = py_version[0] == 3

if not PY3:
    raise RuntimeError('On Python 3')

version = "1.0.0"
here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()


setup(
    name="docmongo",
    version=version,
    description=('A high abastract architecture with pymongo'),
    long_description=README,
    keywords=["mongodb", "mongo", "pymongo"],
    license="Apache License, Version 2.0",
    author="Sato Shun",
    author_email="shun.sato1@gmail.com",
    url="https://github.com/satoshun/docmongo",
    install_requires = install_requires,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
    ],
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
)
