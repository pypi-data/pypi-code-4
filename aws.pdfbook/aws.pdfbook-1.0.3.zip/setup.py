"""aws.pdfbook"""

from setuptools import setup, find_packages
import os

def _textFromPath(*names):
    here = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(here, *names)
    return open(path, 'r').read().strip()

version = '1.0.3'

setup(
    name='aws.pdfbook',
    version=version,
    description="Download Plone content views as PDF",
    long_description='\n\n'.join([
        _textFromPath('README.txt'),
        _textFromPath('docs', 'HISTORY.txt')]),
    # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Programming Language :: Python",
        "Framework :: Plone",
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent"
        ],
    keywords='pdf plone',
    author='Alter Way Solutions',
    author_email='support@ingeniweb.com',
    url='http://pypi.python.org/pypi/aws.pdfbook',
    license='GPL',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['aws'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        # -*- Extra requirements: -*-
        ],
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    """
    )
