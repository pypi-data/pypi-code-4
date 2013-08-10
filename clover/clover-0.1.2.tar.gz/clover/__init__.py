from __future__ import absolute_import
import os
import logging


DIR = os.path.dirname(os.path.abspath(__file__))
CLOSURE_DIR = os.path.join(DIR, 'closure')
# noinspection PyUnresolvedReferences
CLOSURE_LIBRARY_DIR = os.path.join(DIR, 'closure', 'closure-library')


import os
from pkg_resources import resource_string, resource_exists

__dir__ = os.path.dirname(os.path.abspath(__file__))


def get_package_resource(name):
    path = os.path.join(__dir__, name)

    if not os.path.exists(path):
        raise Exception("Could not find package resource: %s" % path)

    return path