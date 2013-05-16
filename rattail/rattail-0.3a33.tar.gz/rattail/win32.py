#!/usr/bin/env python
# -*- coding: utf-8  -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2012 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU Affero General Public License as published by the Free
#  Software Foundation, either version 3 of the License, or (at your option)
#  any later version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for
#  more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################

"""
``rattail.win32`` -- Windows Platform Utilities
"""


def process_is_elevated():
    """
    Check if the current process is running with an "elevated token."

    This is meant to indicate whether administrative privileges are in effect.
    Returns a boolean value.
    """

    from win32api import GetCurrentProcess
    from win32security import OpenProcessToken, GetTokenInformation, TokenElevation
    from win32con import TOKEN_READ

    hProcess = GetCurrentProcess()
    hToken = OpenProcessToken(hProcess, TOKEN_READ)
    elevated = GetTokenInformation(hToken, TokenElevation)
    return bool(elevated)


def require_elevation():
    """
    Exit properly if the current process does not have an "elevated token."

    If the result of :func:`process_is_elevated()` is ``False``, this function
    will print a brief message to ``sys.stderr`` and exit with the error code
    recommended by Microsoft for this scenario.
    """

    import sys
    from winerror import ERROR_ELEVATION_REQUIRED

    if process_is_elevated():
        return

    sys.stderr.write("This command requires administrative privileges.\n")
    sys.exit(ERROR_ELEVATION_REQUIRED)
