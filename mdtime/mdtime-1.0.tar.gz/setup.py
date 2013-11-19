from setuptools import setup, find_packages

setup(name='mdtime',
      version='1.0',
      author='Zhuyi Xue',
      author_email='zhuyi.xue@mail.utoronto.ca',
      url='http://www.zhuyixue.com',
      keywords = 'molecular dynamics gromacs time',
      license='GPLv3',
      description='mdtime checks the time of a tpr file or cpt file, or compare the two to see if cpt < tpr',
      long_description='supposed to be a long description',
      platforms=['unix-like'],

      packages=find_packages(),
      scripts=['mdtime.py']
      )
