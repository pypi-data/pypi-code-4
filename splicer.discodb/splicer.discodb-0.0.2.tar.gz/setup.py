import os.path
from setuptools import setup

HERE = os.path.abspath(os.path.dirname(__file__))

README_PATH = os.path.join(HERE, 'README.md')
try:
    README = open(README_PATH).read()
except IOError:
    README = ''


setup(
  name='splicer.discodb',

  version='0.0.2',
  description='the world is a database',
  long_description=README,
  author='Scott Robertson',
  author_email='scott@triv.io',
  url='http://github.com/trivio/splicer_discodb',
  classifiers=[
      "Programming Language :: Python",
      "License :: OSI Approved :: MIT License",
      "Operating System :: OS Independent",
      "Development Status :: 3 - Alpha",
      "Intended Audience :: Developers",
      "Topic :: Software Development",
  ],

  py_modules = ['splicer_discodb'],

  dependency_links = [
    'https://github.com/trivio/discodb/tarball/master#egg=discodb-0.1'
  ],

  install_requires = [
    'splicer',
    'discodb'
  ],
 
  setup_requires=[
    'nose>=1.3.0',
    'coverage'
  ]
)
