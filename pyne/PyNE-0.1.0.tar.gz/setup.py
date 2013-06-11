__version__ = '0.1.0'

from setuptools import setup

if __name__ == '__main__':
  setup(
    name='PyNE',
    description='A process networking library.',
    author='Jordan Halterman',
    version=__version__,
    author_email='jordan.halterman@gmail.com',
    url='https://github.com/jordanhalterman/pyne',
    keywords=['pyne', 'processing', 'multiprocessing', 'queue'],
    py_modules=['pyne'],
    classifiers=[
      'Development Status :: 3 - Alpha',
      'Environment :: Console',
      'Intended Audience :: Developers',
      'Operating System :: OS Independent',
      'Programming Language :: Python',
      'Programming Language :: Python :: 2.5',
      'Programming Language :: Python :: 2.6',
      'Programming Language :: Python :: 2.7',
      'Programming Language :: PHP',
      'Natural Language :: English',
      'Topic :: Software Development :: Libraries :: Python Modules',
    ])
