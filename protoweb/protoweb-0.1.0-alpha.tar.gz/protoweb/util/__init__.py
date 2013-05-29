# -*- coding: utf-8 -*-
# Copyright 2013 Richard Kuesters.  See LICENSE file for details

from __future__ import absolute_import

import os

from .options import get_options
from .runnable import run

"""
taken from: http://stackoverflow.com/a/377028
"""


def is_exe(fpath):
    return os.path.isfile(fpath) and os.access(fpath, os.X_OK)


def which(program):
    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file
    return None


__all__ = ['which', 'get_options', 'run']
