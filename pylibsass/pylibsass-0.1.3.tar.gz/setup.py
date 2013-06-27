import os
import sys

from setuptools import Extension, setup
from setuptools.command.test import test as TestCommand

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

execfile('pylibsass/version.py')

class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest, sys

        errno = pytest.main(self.test_args)
        sys.exit(errno)

libsass_sources = [
    'libsass/constants.cpp', 'libsass/context.cpp', 'libsass/functions.cpp', 'libsass/document.cpp',
    'libsass/document_parser.cpp', 'libsass/eval_apply.cpp', 'libsass/node.cpp',
    'libsass/node_factory.cpp', 'libsass/node_emitters.cpp', 'libsass/prelexer.cpp',
    'libsass/selector.cpp', 'libsass/sass_interface.cpp', 'libsass/sass_values.cpp',
]

libsass_headers = [
    'libsass/backtrace.hpp', 'libsass/context.hpp', 'libsass/environment.hpp',
    'libsass/eval_apply.hpp', 'libsass/node.hpp', 'libsass/prelexer.hpp',
    'libsass/sass_values.h', 'libsass/color_names.hpp', 'libsass/constants.hpp',
    'libsass/document.hpp', 'libsass/error.hpp', 'libsass/functions.hpp',
    'libsass/node_factory.hpp', 'libsass/sass_interface.h', 'libsass/selector.hpp',
]

sass_extension = Extension(
    'sass',
    libsass_sources,
    define_macros=[('LIBSASS_PYTHON_VERSION', __version__)],
    depends=libsass_headers,
    extra_compile_args=['-Wall', '-O2', '-fPIC'],
    extra_link_args=['-fPIC'],
)

with open("README.rst", 'r') as readme_file:
    readme = readme_file.read()

with open("LICENSE", 'r') as license_file:
    license = license_file.read()

setup(
    name='pylibsass',
    version=__version__,
    url='http://github.com/rsenk330/pylibsass',
    license=license,
    author='Ryan Senkbeil',
    author_email='rsenk330@gmail.com',
    description='Python wrapper for libsass',
    long_description=readme,
    ext_modules=[sass_extension],
    packages=['pylibsass'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    cmdclass = {'test': PyTest},
    tests_require=[
        'pytest',
        'mock',
    ],
    install_requires=[
        'watchdog',
    ],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
