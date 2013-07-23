from setuptools import setup, find_packages
import os

version = '0.9'


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    read('README.txt')
    + '\n' +
    read('js', 'css3mediaqueries', 'test_css3mediaqueries.txt')
    + '\n' +
    read('CHANGES.txt'))

setup(
    name='js.css3mediaqueries',
    version=version,
    description="Fanstatic packaging of css3-mediaqueries.js.",
    long_description=long_description,
    classifiers=[],
    keywords='',
    author='Thomas Massmann',
    author_email='thomas.massmann@it-spir.it',
    url='https://bitbucket.org/it_spirit/js.css3mediaqueries',
    download_url='http://pypi.python.org/pypi/js.css3mediaqueries',
    license='BSD',
    packages=find_packages(),
    namespace_packages=['js'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'fanstatic',
        'setuptools',
    ],
    entry_points={
        'fanstatic.libraries': [
            'css3mediaqueries = js.css3mediaqueries:library',
        ],
    },
)
