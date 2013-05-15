from setuptools import setup, find_packages
import os

version = '0.1'

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    read('README.txt')
    + '\n' +
    read('js', 'namespace', 'test_namespace.txt')
    + '\n' +
    read('CHANGES.txt'))

setup(
    name='js.namespace',
    version=version,
    description="Fanstatic package providing a small js library for declaring namespaces.",
    long_description=long_description,
    classifiers=[],
    keywords='',
    author='Daniel Havlik',
    author_email='dh@gocept.com',
    license='BSD',
    packages=find_packages(),namespace_packages=['js'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'fanstatic',
        'js.jquery',
        'setuptools',
        ],
    entry_points={
        'fanstatic.libraries': [
            'namespace = js.namespace:library',
            ],
        },
    )
