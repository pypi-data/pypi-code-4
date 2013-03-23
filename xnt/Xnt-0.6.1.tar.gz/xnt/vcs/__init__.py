#!/usr/bin/env python
"""Version Controll Module"""

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

def clone_options(cmd, url, branch=None, dest=None):
    """Build up common options for clone commands"""
    new_cmd = list(cmd)
    if branch:
        new_cmd.append("--branch")
        new_cmd.append(branch)
    cmd.append(url)
    if dest:
        new_cmd.append(dest)
    return new_cmd
