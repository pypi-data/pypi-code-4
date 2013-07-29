from setuptools import setup, find_packages
import os

version = '4.2.1'


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    read('README.txt')
    + '\n' +
    read('js', 'fotorama', 'test_fotorama.txt')
    + '\n' +
    read('CHANGES.txt'))

setup(
    name='js.fotorama',
    version=version,
    description="Fanstatic packaging of fotorama.js.",
    long_description=long_description,
    classifiers=[],
    keywords='',
    author='Thomas Massmann',
    author_email='thomas.massmann@it-spir.it',
    url='https://bitbucket.org/it_spirit/js.fotorama',
    download_url='http://pypi.python.org/pypi/js.fotorama',
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
            'fotorama = js.fotorama:library',
        ],
    },
)
