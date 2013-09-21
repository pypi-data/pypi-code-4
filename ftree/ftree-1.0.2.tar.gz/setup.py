from setuptools import setup

setup(
    name='ftree',
    version='1.0.2',
    author='Victor Kindhart',
    author_email='digitloft@gmail.com',
    url='https://pypi.python.org/pypi/ftree',
    scripts=["ftree.py"],
    install_requires=[],
    license='GPL',
    description='Create a File Tree from directory listing.',
    long_description=open('README.rst').read(),
    classifiers=["Environment :: Console", "Programming Language :: Python"],
    )
