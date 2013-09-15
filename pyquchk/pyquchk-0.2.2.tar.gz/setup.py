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
    version='0.2.2',
    packages=find_packages(),
    url='',
    license='',
    author='Alexander Plavin',
    author_email='alexander@plav.in',
    description='Easy-to-use, extensible random testing library.',
    long_description=long_description,
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Testing',
    ],
    tests_require=['nose'],
    install_requires=['six', 'decorator'],
    cmdclass={'test': Tox},
)
