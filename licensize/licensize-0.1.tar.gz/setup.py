from setuptools import setup
from os import path


try:
    README = open(path.join(
        path.dirname(__file__), "README.md")).read()
except IOError:
    README = ''

setup(name='licensize',
        version='0.1',
        description='Little tool that adds a FOSS licenses to your directory.',
        long_description=README,
        url='http://bitbucket.com/michaelb/licensize/',
        author='michaelb',
        author_email='michaelpb@gmail.com',
        license='LGPL 3.0',
        #scripts=['bin/licensize'],
        entry_points = {
                'console_scripts': ['licensize=licensize:main'],
            },
        packages=['licensize'],
        zip_safe=False)

