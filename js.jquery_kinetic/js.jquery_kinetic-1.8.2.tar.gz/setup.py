from setuptools import setup, find_packages
import os

version = '1.8.2'


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    read('README.txt')
    + '\n' +
    read('js', 'jquery_kinetic', 'test_kinetic.txt')
    + '\n' +
    read('CHANGES.txt'))

setup(
    name='js.jquery_kinetic',
    version=version,
    description="fanstatic packaging of jquery.kinetic",
    long_description=long_description,
    classifiers=[],
    keywords='fanstatic, jquery, javascript',
    author='Sebastien Douche',
    author_email='sdouche@gmail.com',
    url='http://davetayls.me/jquery.kinetic/',
    license='BSD',
    packages=find_packages(),
    namespace_packages=['js'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'fanstatic',
        'setuptools',
        'js.jquery',
        'js.jqueryui',
    ],
    entry_points={
        'fanstatic.libraries': [
            'jquery.kinetic = js.jquery_kinetic:library',
        ],
    },
)
