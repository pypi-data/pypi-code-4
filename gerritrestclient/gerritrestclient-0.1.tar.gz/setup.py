from setuptools import setup

setup(name='gerritrestclient',
      version='0.1',
      description='Client for Gerrit Code Review REST API',
      url='http://github.com/lann/gerritrestclient',

      install_requires=['simplemodel'],

      author='Lann Martin',
      author_email='gerritrestclient@lannbox.com',
      license='MIT',
      packages=['gerritrestclient'])
