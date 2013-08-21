from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
import sys


class Tox(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import tox

        errno = tox.cmdline(self.test_args)
        sys.exit(errno)


with open('README.rst') as file:
    long_description = file.read()

setup(
    name='pyquchk',
    version='0.1.1',
    packages=find_packages(),
    url='',
    license='',
    author='Alexander Plavin',
    author_email='alexander@plav.in',
    description='Easy-to-use, extensible random testing (insired by QuickCheck) library.',
    long_description=long_description,
    tests_require=['nose'],
    install_requires=['six', 'decorator'],
    cmdclass={'test': Tox},
)
