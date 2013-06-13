from os.path import exists
from setuptools import setup

setup(name='posort',
      version='0.1',
      description='Partially ordered sort',
      url='http://github.com/mrocklin/posort',
      author='Matthew Rocklin',
      author_email='mrocklin@gmail.com',
      license='BSD',
      packages=['posort'],
      long_description=open('README.md').read() if exists("README.md") else "",
      zip_safe=False)
