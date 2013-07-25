from setuptools import setup, find_packages
import os

version = '0.1'


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    read('README.txt')
    + '\n' +
    read('js', 'jquery_interdependencies', 'test_jquery_interdependencies.txt')
    + '\n' +
    read('CHANGES.txt'))

setup(
    name='js.jquery_interdependencies',
    version=version,
    description="Fanstatic packaging of jQuery Interdependencies.",
    long_description=long_description,
    classifiers=[],
    keywords='',
    author='Thomas Massmann',
    author_email='thomas.massmann@it-spir.it',
    url='https://bitbucket.org/it_spirit/js.jquery_interdependencies',
    download_url='http://pypi.python.org/pypi/js.jquery_interdependencies',
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
            'jquery_interdependencies = js.jquery_interdependencies:library',
        ],
    },
)
