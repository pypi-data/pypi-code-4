from setuptools import setup
from boxmath import __version__
import os

try:
    from setuptools.command.test import test
except ImportError:
    cmdclass = {}
else:
    class pytest(test):

        def finalize_options(self):
            test.finalize_options(self)
            self.test_args = []
            self.test_suite = True

        def run_tests(self):
            from pytest import main
            errno = main(self.test_args)
            raise SystemExit(errno)
    cmdclass = {'test': pytest}

def readme():
    with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as f:
        return f.read()

setup(
    name="boxmath",
    version=__version__,
    description="Simple image box arithmetic",
    license="BSD License",
    author="Eric Moritz",
    author_email="eric@themoritzfamily.com",
    maintainer="Eric Moritz",
    maintainer_email="eric@themoritzfamily.com",
    url="http://github.com/ericmoritz/boxmath",
    long_description=readme(),
    packages=["boxmath"],
    tests_require=["pytest", "pytest-quickcheck"],
    cmdclass=cmdclass,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Programming Language :: Python :: Implementation :: Stackless',
        'Topic :: Multimedia :: Graphics'
    ]
)
