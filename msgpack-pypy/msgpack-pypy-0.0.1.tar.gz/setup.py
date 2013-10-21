import sys
import os.path
from setuptools import setup, find_packages

readme = os.path.join(os.path.dirname(__file__), 'README')
long_description = open(readme).read()

setup(
    name='msgpack-pypy',
    version='0.0.1',
    author='Antonio Cuni',
    author_email='anto.cuni@gmail.com',
    py_modules=['msgpack_pypy'],
    url='http://bitbucket.org/antocuni/msgpack-pypy',
    license='BSD',
    platforms=['unix', 'linux', 'osx', 'cygwin', 'win32'],
    description='A msgpack extension with special optimizations for PyPy',
    long_description=long_description,
    keywords='msgpack PyPy',
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
        "Intended Audience :: Developers",
        "Operating System :: POSIX",
        "Topic :: Utilities",
        ],
    install_requires=["msgpack-python>=0.4"],
)
