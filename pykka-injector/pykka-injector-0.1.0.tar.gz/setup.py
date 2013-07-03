from os.path import abspath, dirname, join

from setuptools import setup

PROJECT_ROOT = abspath(dirname(__file__))

long_description = open(join(PROJECT_ROOT, 'README.rst')).read()
description = 'Pykka/Injector integration module'

module_code = open(join(PROJECT_ROOT, 'pykka_injector.py')).readlines()
line = [line for line in module_code if line.startswith('__version__ = ')][0]
version = line.split('=')[-1].strip().strip("'")

if __name__ == '__main__':
    setup(
        name='pykka-injector',
        url='http://github.com/jstasiak/pykka-injector',
        download_url='http://pypi.python.org/pypi/pykka-injector',
        version=version,
        description=description,
        long_description=long_description,
        license='MIT',
        platforms=['any'],
        py_modules=['pykka_injector'],
        author='Jakub Stasiak',
        author_email='jakub@stasiak.at',
        install_requires=[
            'setuptools >= 0.6b1',
            'pykka',
            'injector',
        ],
    )
