from setuptools import setup, find_packages

KEYWORDS = 'injection ioc container plugin discovery service contract hk2 kernel'.split(' ')
SUMMARY = 'Hundred-Kilobyte Kernel library for dependency injection and service discovery'
DESCRIPTION = '''Python Hundred-Kilobyte Kernel library.

It is inspired by HK2 library for Java that allows easily create plug-in based applications.'''

setup(name='pyhk2',
      version='0.0.1',
      url='https://github.com/mikhtonyuk/pyhk2',
      author='Sergii Mikhtoniuk',
      author_email='mikhtonyuk@gmail.com',
      license='MIT',
      description=SUMMARY,
      long_description=DESCRIPTION,
      keywords=KEYWORDS,
      packages=find_packages(exclude=['test*']),
      zip_safe=False,
      test_suite='test')