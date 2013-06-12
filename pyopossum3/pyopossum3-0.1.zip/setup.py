from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest  # import here, cause outside the eggs aren't loaded
        pytest.main(self.test_args)

version = '0.1'

setup(name='pyopossum3',
      version=version,
      description="SQLAlchemy-based interface to the oPOSSUM3 transcription factor binding database.",
      long_description=open("README.rst").read(),
            classifiers=[  # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Science/Research',
          'License :: OSI Approved :: MIT License',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 2',
          'Topic :: Scientific/Engineering :: Bio-Informatics'
      ],
      platforms=['Platform Independent'],
      keywords='bioinformatics oPOSSUM3 data-access transcription tfbs',
      author='Konstantin Tretyakov',
      author_email='kt@ut.ee',
      url='https://github.com/konstantint/pyopossum3',
      license='MIT',
      packages=find_packages(exclude=['tests', 'examples']),
      include_package_data=True,
      zip_safe=True,
      install_requires=['SQLAlchemy', 'MySQL-python'],
      tests_require=['pytest'],
      cmdclass={'test': PyTest},
      entry_points=''
      )
