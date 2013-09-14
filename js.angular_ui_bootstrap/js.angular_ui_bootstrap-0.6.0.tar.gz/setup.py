# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import os

# The version of the wrapped library is the starting point for the
# version number of the python package.
# In bugfix releases of the python package, add a '-' suffix and an
# incrementing integer.
# For example, a packaging bugfix release version 1.4.4 of the
# js.jquery package would be version 1.4.4-1 .

version = '0.6.0'

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    read('README.txt') + '\n' +
    read('CHANGES.txt')
)

setup(
    url='https://github.com/abulte/js.angular_ui_bootstrap',
    author=u'Alexandre Bulté',
    author_email='alexandre@bulte.net',
    name='js.angular_ui_bootstrap',
    version=version,
    description="Fanstatic packaging of Angular UI Boostrap",
    long_description=long_description,
    classifiers=[],
    keywords='',
    license='MIT',
    packages=find_packages(),
    namespace_packages=['js'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'fanstatic',
        'js.angular',
        'js.bootstrap',
        'setuptools',
        ],
    entry_points={
        'fanstatic.libraries': [
            'angularuibootstrap = js.angular_ui_bootstrap:library',
            ],
        },
    )