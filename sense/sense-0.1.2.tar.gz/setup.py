# If you're creating an sdist, do 
# 'pandoc --from=markdown --to=rst --output=README.rst README.md' 
# first to generate the ReST version of the docs.
# Then, make sure docutils is installed and run rst2html.py README.rst, 
# and fix any errors or warnings.

from setuptools import setup
setup(name='sense',
      version='0.1.2',
      author='Sense Inc.',
      author_email='support@senseplatform.com',
      maintainer='Sense Inc.',
      maintainer_email='support@senseplatform.com',
      platforms=['Sense'],
      url='https://www.senseplatform.com',
      license='MIT',
      description='Standard Sense utilities for Python',
      py_modules=['sense'])
