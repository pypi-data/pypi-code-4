import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

setup(
    name='collagram',
    version='0.6',
    author='Adam Patterson',
    author_email='adam@adamrt.com',
    url='http://github.com/vurbmedia/collagram/',
    license='ISC',
    description='Generate collages of Instagram photographs.',
    packages=['collagram'],
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=[
        'Pillow',
        'python-instagram'
    ],
)
