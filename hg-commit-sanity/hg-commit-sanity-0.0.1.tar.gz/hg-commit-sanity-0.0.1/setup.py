import os
import sys

from setuptools import setup
from setuptools.command.test import test as TestCommand


class Tox(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = ['--recreate']
        self.test_suite = True

    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import tox
        errno = tox.cmdline(self.test_args)
        sys.exit(errno)


dirname = os.path.dirname(__file__)

long_description = (
    open(os.path.join(dirname, 'README.rst')).read() + '\n' +
    open(os.path.join(dirname, 'CHANGES.rst')).read()
)

setup(
    name='hg-commit-sanity',
    description='Mercurial extension to do sanity checks on commits.',
    long_description=long_description,
    license='MIT license',
    author='Anatoly Bubenkov on behalf of Paylogic International',
    author_email='developer@paylogic.com',
    url='https://github.com/paylogic/hg-commit-sanity',
    version='0.0.1',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: MacOS :: MacOS X',
        'Topic :: Software Development :: Version Control',
        'Topic :: Utilities',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3'
    ] + [('Programming Language :: Python :: %s' % x) for x in '2.6 2.7 3.0 3.1 3.2 3.3'.split()],
    cmdclass={'test': Tox},
    install_requires=[
        'mercurial'
    ],
    tests_require=['tox'],
)
