#!/usr/bin/env python
"""CVS Version Control Wrapper"""

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

def cvsco(module, rev="", dest=""):
    """Run CVS Checkout

    :param module: CVS Module name to checkout
    :param rev: Revision to checkout
    :param dest: Destination directory or name of checked out module
    """
    assert which("cvs")
    cmd = ["cvs", "co", "-P"]
    if rev:
        cmd.append("-r")
        cmd.append(rev)
    if dest:
        cmd.append("-d")
        cmd.append(dest)
    cmd.append(module)
    subprocess.call(cmd)

def cvsupdate(path):
    """Run CVS Update

    :param path: Directory path to module to update
    """
    assert which("cvs")
    cwd = os.path.abspath(os.getcwd())
    os.chdir(path)
    cmd = ["cvs", "update"]
    subprocess.call(cmd)
    os.chdir(cwd)
