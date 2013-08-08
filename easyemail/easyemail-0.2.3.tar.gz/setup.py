from setuptools import setup
from setuptools.command.test import test as TestCommand
import os
import sys


def read(filename):
    """Open a file and return its contents."""
    with open(os.path.join(os.path.dirname(__file__), filename)) as f:
        return f.read()


class PyTest(TestCommand):
    """Command to run unit tests after in-place build."""

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = ['tests']
        self.test_suite = True

    def run_tests(self):
        # Importing here, `cause outside the eggs aren't loaded.
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)


setup(
    name='easyemail',
    version='0.2.3',
    description="Simple lib abstracting email sending with smtplib.",
    long_description=read('README.md'),
    url='http://github.com/niktto/easyemail/',
    license=read('LICENSE'),
    author=u'Marek Szwalkiewicz',
    author_email='marek@szwalkiewicz.waw.pl',
    packages=['easyemail'],
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=[],
    tests_require=['pytest', 'Jinja2>=2.7.1', 'Mako>=0.7.3'],
    cmdclass={'test': PyTest},
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
)
