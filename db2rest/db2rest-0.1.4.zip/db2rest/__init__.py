# -*- coding: utf-8 -*-
"""
db2rest
~~~~~~~
A HTTP REST API for relational databases

:copyright: (c) 2013 by Functional Genomic Center Zurich, Nicola Palumbo.

:license: MIT, see LICENSE for more details.
"""
import os
from . import version

module_dir = os.path.sep.join(__file__.split(os.path.sep)[:-1])
module_doc = os.path.sep.join(__file__.split(os.path.sep)[:-2] + ['doc'])
file_name = version.__file__

__version__ = version.vers
