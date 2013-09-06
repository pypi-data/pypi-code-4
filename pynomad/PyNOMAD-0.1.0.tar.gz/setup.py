from setuptools import setup

setup(name='PyNOMAD',
      version='0.1.0',
      description='Routines for accessing a self-hosted local copy of the USNO NOMAD stellar catalog',
      long_description=open('README.txt').read(),
      author='Henry Roe',
      author_email='hroe@hroe.me',
      url='http://pypi.python.org/pypi/PyNOMAD',
      license='LICENSE.txt',
      py_modules=['nomad', 'nomad_test'],
      install_requires=['pandas>=0.10.1'])
