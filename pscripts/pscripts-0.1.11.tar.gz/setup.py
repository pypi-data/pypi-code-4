from setuptools import setup
version='0.1.11'
name='pscripts'
scripts = ['scripts/python-deployment']
classifiers = [
        'Programming Language :: Python :: 3.3',
    ]
setup(
    name = name,
    version = version,
    packages = [name],
    description = 'Weechat Notification Plugin',
    author='Fenton Travers',
    author_email='fenton.travers@gmail.com',
    url='www.google.com',
    license='Creative Commons Attribution-Noncommercial-Share Alike license',
    long_description='Some description',
    classifiers=classifiers,
    scripts = scripts
)
