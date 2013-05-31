import os
import sys

from setuptools import setup


if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

setup(
    name='collagram',
    version='0.7.1',
    author='Adam Patterson',
    author_email='adam@adamrt.com',
    url='http://github.com/vurbmedia/collagram/',
    license='ISC',
    description='Generate collages of Instagram photographs.',
    py_modules=['collagram'],
    zip_safe=False,
    platforms='any',
    install_requires=[
        'Pillow',
        'python-instagram'
    ],
)
