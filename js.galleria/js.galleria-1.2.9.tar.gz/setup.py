from setuptools import setup, find_packages
import os

version = '1.2.9'


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    read('README.txt')
    + '\n' +
    read('js', 'galleria', 'test_galleria.txt')
    + '\n' +
    read('CHANGES.txt'))

setup(
    name='js.galleria',
    version=version,
    description="Fanstatic packaging of galleria.js.",
    long_description=long_description,
    classifiers=[],
    keywords='',
    author='Thomas Massmann',
    author_email='thomas.massmann@it-spir.it',
    url='https://bitbucket.org/it_spirit/js.galleria',
    download_url='http://pypi.python.org/pypi/js.galleria',
    license='BSD',
    packages=find_packages(),
    namespace_packages=['js'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'fanstatic',
        'js.jquery',
        'setuptools',
    ],
    entry_points={
        'fanstatic.libraries': [
            'galleria = js.galleria:library',
        ],
    },
)
