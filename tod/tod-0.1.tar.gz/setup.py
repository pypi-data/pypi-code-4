from tod import __version__
try:
        from setuptools import setup
except ImportError:
        from distutils.core import setup

description = """\
A simple dotfiles manager.  Uses symlinks and a git repo."""

setup(
    name='tod',
    version=__version__,
    url='https://github.com/mvliet/tod',
    description=description,
    long_description=open('README.rst').read(),
    author='Matthew Vliet',
    author_email='matt.vliet@gmail.com',
    packages=['tod'],
    license='MIT',
    scripts=['scripts/tod'],
    install_requires=['termcolor'],
    zip_safe=False,
    include_package_data=True,
    package_data={ '': ['README.rst'] },
)

