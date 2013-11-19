from setuptools import setup, find_packages

setup(name='mdtime',
      version='1.0.1a1',
      author='Zhuyi Xue',
      author_email='zhuyi.xue@mail.utoronto.ca',
      url='http://www.zhuyixue.com',
      keywords = 'molecular dynamics gromacs time',
      license='GPLv3',
      description='mdtime checks the time of a tpr file or cpt file from Gromacs, or compare the two to see if time in cpt is less than that in tpr',
      long_description='supposed to be a long description',
      platforms=['unix-like'],

      packages=find_packages(),
      scripts=['mdtime.py']
      )
