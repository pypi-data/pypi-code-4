from distutils.core import setup

setup(
    name='Pybles',
    version='1.0.1',
    author='Guido Accardo',
    author_email='gaccardo@gmail.com',
    packages=['pybles'],
    url='http://pypi.python.org/pypi/Pybles/',
    license='LICENSE.txt',
    description='Module to represent tables in the terminal using pyton',
    long_description=open('README.txt').read(),
    install_requires=[
        "blessings >= 1.5.1",
    ],)
