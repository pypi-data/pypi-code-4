# -*- coding: utf-8 -*-
__revision__ = "$Id: $"

import sys
import os

from setuptools import setup, find_packages



#The metainfo files must contains 'metainfo.ini'
# version, release, project, name, namespace, pkg_name,
# description, long_description,
# authors, authors_email, url and license

# name will determine the name of the egg, as well as the name of 
# the pakage directory under Python/lib/site-packages). It is also 
# the one to use in setup script of other packages to declare a dependency to this package)
# (The version number is used by deploy to detect UPDATES)
import ConfigParser
conf = ConfigParser.RawConfigParser()
conf.read('metainfo.ini')
metadata = dict([(key,conf.get('metainfo',key)) for key in conf.options('metainfo')])

print '*** Installing the following package: ***'
for key,value in metadata.items():
    key = str(key)
    print '\t', key+':\t', value


# setup dependencies stuff
setup_requires   = []
install_requires = []
dependency_links = []

# generate openalea wrapper and entry points
#  ------------------------------------------
sys.path.insert(0,os.path.abspath('src'))
import ndarray
from ndarray.openalea import wrap_package, clean_wralea_package

# clear previously generated wralea folder
left = clean_wralea_package('rhizoscan_wralea')

if left:
    print '\n not generated files in wralea folder'
    print '\n'.join(left)
else:
    print '\n wralea folder is empty'
    
# generate wralea packages
entry =  wrap_package(ndarray,entry_name='ndarray',verbose=0)
print '\n wralea entry found:\n' + '\n'.join(entry) + '\n'

entry_points = {}
if entry:
    entry_points['wralea'] = entry


# call setup
# ----------
setup(
    name            = metadata['name'],
    version         = metadata['version'],
    description     = metadata['description'],
    long_description= metadata['long_description'],
    author          = metadata['authors'],
    url             = metadata['url'],
    license         = metadata['license'],
    keywords        = metadata.get('url',''),	
    
    # package installation
    packages=    find_packages('src'),	
    package_dir= dict([('','src')]),
    
    # Dependencies
    setup_requires   = setup_requires,
    install_requires = install_requires,
    dependency_links = dependency_links,

    # Eventually include data in your package
    # (flowing is to include all versioned files other than .py)
    include_package_data = True,
    # (you can provide an exclusion dictionary named exclude_package_data to remove parasites).
    # alternatively to global inclusion, list the file to include   
    package_data = {'' : [ '*.ini' ],},

    # Declare scripts and wralea as entry_points (extensions) 
    entry_points = entry_points,
    )



