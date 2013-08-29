import os
import sys
from setuptools import setup, find_packages

execfile(os.path.join("abl", "jquery", "core", "release.py"))

setup(
    name=__PROJECT__,
    version=__VERSION__,
    description=__DESCRIPTION__,
    author=__AUTHOR__,
    author_email=__EMAIL__,
    url=__URL__,
    license=__LICENSE__,
    download_url='http://bitbucket.org/deets/abljquery/downloads/',
    install_requires=[
        "ToscaWidgets>0.9.7",
        ## Add other requirements here
        # "Genshi",
        ],
    packages=find_packages(exclude=['ez_setup', 'tests']),
    package_data = {'': ['*.html', '*.txt', '*.rst']},
    namespace_packages = ['abl', 'abl.jquery', 'abl.utils', 'abl.jquery.plugins', 'abl.jquery.examples'],
    zip_safe=False,
    include_package_data=True,
    test_suite = 'nose.collector',
    entry_points="""
    [toscawidgets.widgets]
    widgets = abl.jquery.core
    resource_aggregation_filter = abl.jquery.core.base:filter_resources
    """,
    keywords = [
        'toscawidgets.widgets',
    ],
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Environment :: Web Environment :: ToscaWidgets',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Widget Sets',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
)
