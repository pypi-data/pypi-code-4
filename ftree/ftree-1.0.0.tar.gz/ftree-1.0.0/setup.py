from setuptools import setup, find_packages

setup(
    name='ftree',
    version='1.0.0',
    author='Victor Kindhart',
    author_email='digitloft@gmail.com',
    url='https://pypi.python.org/pypi/ftree',
    packages=find_packages(),
    install_requires=[],
    license='GPL',
    description='Create a File Tree from directory listing',
    long_description=open('README.rst').read(),
    classifiers=["Environment :: Console", "Programming Language :: Python"],
    )
