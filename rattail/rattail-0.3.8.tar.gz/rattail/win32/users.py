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
``rattail.win32.users`` -- Windows User Utilities
"""

import socket
import logging


log = logging.getLogger(__name__)


def create_rattail_user(password):
    """
    Create a system user account for Rattail.
    """

    import win32net
    import win32netcon

    if user_exists('rattail'):
        log.warning("create_rattail_user: user 'rattail' already exists")
        return False

    win32net.NetUserAdd(None, 2, {
            'name': 'rattail',
            'password': password,
            'priv': win32netcon.USER_PRIV_USER,
            'comment': "System user account for Rattail applications",
            'flags': (win32netcon.UF_NORMAL_ACCOUNT
                      | win32netcon.UF_PASSWD_CANT_CHANGE
                      | win32netcon.UF_DONT_EXPIRE_PASSWD),
            'full_name': "Rattail User",
            'acct_expires': win32netcon.TIMEQ_FOREVER,
            })

    win32net.NetLocalGroupAddMembers(None, 'Users', 3, [
            {'domainandname': r'{0}\rattail'.format(socket.gethostname())}])

    hide_user_account('rattail')
    return True


def hide_user_account(username):
    """
    Hide a user account from the Welcome screen.

    This also hides it from the User Accounts control panel applet.
    """

    import win32api
    import win32con

    key = win32api.RegOpenKeyEx(
        win32con.HKEY_LOCAL_MACHINE,
        r'SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon\SpecialAccounts\UserList',
        0, win32con.KEY_ALL_ACCESS)

    win32api.RegSetValueEx(key, username, 0, win32con.REG_DWORD, 0)
    win32api.RegCloseKey(key)


def user_exists(username):
    """
    Determine if a system user account already exists.
    """

    import win32net
    from pywintypes import error

    # This constant doesn't seem to be importable from anywhere.
    NERR_UserNotFound = 2221

    try:
        info = win32net.NetUserGetInfo(None, username, 1)
    except error, e:
        if e.winerror == NERR_UserNotFound:
            return False
        raise
    return True
