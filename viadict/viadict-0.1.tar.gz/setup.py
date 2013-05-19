from setuptools import setup

setup(name='viadict',
      version='0.1',
      description='ViaDict is a command-line interface to the OS X Dictionary service.',
      url='http://github.com/nickbarnwell/viadict',
      author='Nicholas Barnwell',
      author_email='nb@ul.io',
      license='MIT',
      platforms=['darwin'],
      packages=['viadict'],
      scripts=['bin/viadict'],
      zip_safe=False)
