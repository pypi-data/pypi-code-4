
################################################################
# pp.core - Produce & Publish
# (C) 2013, ZOPYX Limited, www.zopyx.com
################################################################
""" 
Resources registry for templates, styles etc.
"""

import os
from fs.osfs import OSFS
from pp.core.logger import  LOG
from pp.core.resource import Resource

# mapping name -> directory
resources_registry = dict()

def registerResource(name, directory):
    if not os.path.exists(directory):
        raise IOError('Directory "{}" does not exit'.format(directory))
    if name in resources_registry:
        raise KeyError('A resource "{}" is already registered'.format(name))
    resources_registry[name] = Resource(OSFS(directory))
    LOG.info('Registered resource directory "{}" as "{}"'.format(directory, name))
