import os

from setuptools import setup, find_packages


def read(filename):
    """Open a file and return its contents."""
    return open(os.path.join(os.path.dirname(__file__), filename)).read()


setup(
    name='twcli',
    version='2.0',
    description='TaskWorkshop CLI',
    long_description=read('README.rst'),
    author='Altermind',
    author_email='contact@altermind.pl',
    url='https://github.com/taskworkshop/taskworkshop-cli',
    license=read('LICENSE'),
    scripts=['scripts/tw'],
    packages=find_packages(exclude=['tests']),
    zip_safe=False,
    classifiers=[
        'Programming Language :: Python :: 2.7',
        'Environment :: Console',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Operating System :: POSIX',
        'Topic :: Software Development :: Bug Tracking'
    ]
)
