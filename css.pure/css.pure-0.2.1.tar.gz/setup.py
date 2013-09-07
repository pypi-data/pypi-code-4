from setuptools import setup, find_packages
import os

version = '0.2.1'


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    read('README.rst')
    + '\n' +
    read('CHANGES.rst'))

setup(
    name='css.pure',
    version=version,
    description="Pure CSS for Fanstatic",
    long_description=long_description,
    classifiers=[],
    keywords='',
    author='Ole Morten Halvorsen',
    author_email='olemortenh@gmail.com',
    url='https://bitbucket.org/fanstatic/js.jquery',
    license='BSD',
    packages=find_packages(),
    namespace_packages=['css'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'fanstatic',
        'setuptools',
    ],
    entry_points={
        'fanstatic.libraries': [
            'pure = css.pure:library',
        ],
    },
)
