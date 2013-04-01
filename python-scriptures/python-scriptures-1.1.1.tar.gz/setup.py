from distutils.core import setup

setup(
    name='python-scriptures',
    version='1.1.1',
    author='David Davis',
    author_email='davisd@davisd.com',
    packages=['scriptures',],
    url='http://www.davisd.com/projects/python-scriptures/',
    data_files=[('.',['LICENSE'])],
    license='LICENSE',
    description='python-scriptures is a Python package and regular ' \
        'expression library for validating, extracting, and normalizing ' \
        'biblical scripture references from blocks of text.',
    long_description=open('README').read(),
)

