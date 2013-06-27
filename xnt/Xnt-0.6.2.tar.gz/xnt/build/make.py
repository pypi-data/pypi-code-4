#!/usr/bin/env python
"""Wrapping methods around build tools"""

#   Xnt -- A Wrapper Build Tool
#   Copyright (C) 2013  Kenny Ballou

#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.

#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.

#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import subprocess
from xnt.tasks import which

def ant(target, path="", flags=None, pkeys=None, pvalues=None):
    """Wrapper around Apache Ant

    Invoke Apache Ant in either the current working directory or the specified
    directory using the specified target, passing a list of *flags* to the
    invocation. Where *flags* is a list of valid flags for *ant*.

    `pkeys` and `pvalues` are zipped to form a key/value pair passed to Ant as
    property values

    :param target: Ant Target to execute
    :param path: Path of the Ant build file if different than current directory
    :param flags: List of flags to pass to Ant
    :param pkeys: List of keys to combine with pvalues to pass to Ant
    :param pvalues: List of values to combine with pkeys to pass to Ant
    """
    assert which("ant")
    cmd = __add_params(["ant"],
                       __build_param_list(pkeys, pvalues),
                       lambda x: "-D%s" % x)
    cmd = __add_flags(cmd, flags)
    cmd.append(target)
    return __run_in(path, lambda: subprocess.call(cmd))

def make(target, path="", flags=None, pkeys=None, pvalues=None):
    """Wrapper around GNU Make

    Invoke Gnu Make (*make*) in either the current working directory or the
    specified directory using the specified target, passing a list of *flags*
    to the invocation. Where *flags* is a list of valid flags for *make*.

    `pkeys` and `pvalues` are zipped together to form a key/value pair that are
    passed to Make as property values.

    :param target: Make Target to execute
    :param path: Path of the make file if different than current directory
    :param flags: List of flags to pass to make
    :param pkeys: List of keys, zipped with pvalues, to pass to Make
    :param pvalues: List of values, zipped with pkeys, to pass to Make
    """
    assert which("make")
    cmd = __add_params(["make"], __build_param_list(pkeys, pvalues))
    cmd = __add_flags(cmd, flags)
    cmd.append(target)
    return __run_in(path, lambda: subprocess.call(cmd))

def nant(target, path="", flags=None, pkeys=None, pvalues=None):
    """Wrapper around .NET Ant

    Invoke NAnt in either the current working directory or the specified
    directory using the specified target, passing a list of *flags* to the
    invocation. Where *flags* is a list of valid flags for *nant*.

    `pkeys` and `pvalues` are zipped together to form a key/ value pair to pass
    to NAnt as property values.

    :param target: NAnt Target to execute
    :param path: Path of NAnt build file, if different than current directory
    :param flags: List of flags to pass to NAnt
    :param pkeys: List of keys, zipped with pvalues, to pass to NAnt
    :param pvalues: List of values, zipped with pkeys, to pass to NAnt
    """
    assert which("nant")
    cmd = __add_params(["nant"],
                        __build_param_list(pkeys, pvalues),
                        lambda x: "-D:%s" % x)
    cmd = __add_flags(cmd, flags)
    cmd.append(target)
    return __run_in(path, lambda: subprocess.call(cmd))

def __add_flags(cmd, flags):
    """Add flags to command and return new list"""
    if not flags:
        return cmd
    command = list(cmd)
    for flag in flags:
        command.append(flag)
    return command

def __build_param_list(keys, values):
    """Build a list of key-value for appending to the command list"""
    parameters = []
    if not keys or not values:
        return parameters
    params = zip(keys, values)
    for param in params:
        parameters.append("%s=%s" % param)
    return parameters

def __add_params(cmd, params, param_map=lambda x: x):
    """Append parameters to cmd list using fn"""
    if not params:
        return cmd
    command = list(cmd)
    for param in params:
        command.append(param_map(param))
    return command

def __run_in(path, function):
    """Execute function while in a different running directory"""
    cwd = os.path.abspath(os.getcwd())
    if path and os.path.exists(path):
        os.chdir(os.path.abspath(path))
    result = function()
    if cwd:
        os.chdir(cwd)
    return result
