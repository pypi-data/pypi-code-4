#!/usr/bin/env python

from __future__ import absolute_import

from distutils.core import Command
from distutils.util import convert_path
from distutils.command.build_py import build_py as _build_py

import migrate.versioning.api as dbmigrate

_all__ = [ "migrate", "psql" ]
