from setuptools import setup
from glob import glob

setup(
    name='Pizza.py',
    version='0.1.0',
    author='Steve Plimpton',
    author_email='sjplimp@sandia.gov',
    packages=['pizza', 'pizza.test'],
    url='http://pypi.python.org/pypi/Pizza.py/',
    license='LICENSE.txt',
    description='Tools for working with the LAMMPS molecular dynamics package',
    long_description=open('README.txt').read(),
    install_requires=[
        "numpy"
    ],
    scripts=glob("bin/*.py"),
    data_files=[('pizza/test/files', glob("pizza/test/files/*"))]
)
