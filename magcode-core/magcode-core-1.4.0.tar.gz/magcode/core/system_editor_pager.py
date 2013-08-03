#!/usr/bin/env python3.2
#
# Copyright (c) Net24 Limited, Christchurch, New Zealand 2011-2012
#       and     Voyager Internet Ltd, New Zealand, 2012-2013
#
#    This file is part of py-magcode-core.
#
#    Py-magcode-core is free software: you can redistribute it and/or modify
#    it under the terms of the GNU  General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Py-magcode-core is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU  General Public License for more details.
#
#    You should have received a copy of the GNU  General Public License
#    along with py-magcode-core.  If not, see <http://www.gnu.org/licenses/>.
#
"""
Mixin utility class for determining system pager editor 
"""


import os
import os.path
import sys
import grp
import pwd
from subprocess import Popen
from subprocess import PIPE

from magcode.core.globals_ import settings


LESS_ARGS = '-REX'

class SystemEditorPager(object):
    """
    Mixin class for functions to get system editor/pager
    """

    def check_if_admin(self):
        """
        Checks if the user has group membership that would allow full access
        """
        if not hasattr(self, 'admin_mode') or self.admin_mode == None:
            # Read admin_group_list and resolve it to GIDs
            admin_group_list = settings['admin_group_list'].split()
            admin_group_gids = []
            for g in admin_group_list:
                try:
                    admin_gid = grp.getgrnam(g).gr_gid
                    admin_group_gids.append(admin_gid)
                except KeyError:
                    pass
            process_gids = os.getgroups()
            # Most manpages for getgroups(2) suggest you also check gid and egid
            gid = os.getgid()
            egid = os.getegid()
            if gid and gid not in process_gids:
                process_gids.append(gid)
            if egid and egid not in process_gids:
                process_gids.append(egid)
            result = set(process_gids).intersection(admin_group_gids)
            result = True if len(result) else False
            result = True if os.geteuid == 0 else result
            self.admin_mode = result
        return self.admin_mode

    def get_editor(self):
        """
        Work out the users preference of editor, and return that
        """
        if not self.admin_mode:
            return settings['editor']

        editor = os.getenvb(b'VISUAL')
        if (editor):
            return editor.decode()
    
        editor = os.getenvb(b'EDITOR')
        if (editor):
            return editor.decode()

        editor = '/usr/bin/editor'
        if os.path.isfile(editor):
            return editor 

        # Fall back if none of the above is around...
        return '/usr/bin/vi'

    def get_pager(self):
        """
        Work out the users preference of pager and return that
        """
        pager_args = settings['pager_args']
        if not self.admin_mode:
            pager = settings['pager']
            if (os.path.realpath(pager).endswith('less')
                    and not pager_args):
                settings['pager_args'] = LESS_ARGS
            return settings['pager']

        pager = os.getenvb(b'PAGER')
        if (pager):
            pager = pager.decode()
            if pager.endswith('less') and not pager_args:
                settings['pager_args'] = '-EX'
            return pager

        pager = '/usr/bin/pager'
        if os.path.isfile(pager):
            if (os.path.realpath(pager).endswith('less')
                    and not pager_args):
                settings['pager_args'] = LESS_ARGS
            return pager

        # Fall backs if none of the above is around
        # Try less
        pager = '/usr/bin/less'
        if os.path.isfile(pager):
            if not pager_args:
                settings['pager_args'] = LESS_ARGS
            return pager

        # Try more
        pager = '/usr/bin/more'
        if os.path.isfile(pager):
            return pager
        # In Debian its here...
        pager = '/bin/more'
        if os.path.isfile(pager):
            return pager

        # This is the pathological default...
        return '/bin/cat'

    def get_pager_args(self):
        """
        Return pager args

        MUST be called after get_pager
        """
        pager_args = os.getenvb(b'MAGCODE_PAGER_ARGS')
        # Need to be able to detect environment setting of no args ''
        if (pager_args is not None):
            return pager_args.decode()
        return settings['pager_args']

    def get_diff(self):
        """
        Work out where the system's diff is
        """
        diff = os.getenvb(b'MAGCODE_DIFF')
        if (diff):
            return diff.decode()
        
        # Colorize diff output
        diff = '/usr/bin/colordiff'
        if os.path.isfile(diff):
            return diff
        diff = '/usr/local/bin/colordiff'
        if os.path.isfile(diff):
            return diff

        # where binary is on FreeBSD and Linux
        return '/usr/bin/diff'

    def get_diff_args(self):
        """
        Work out the diff args 
        """
        diff_args = os.getenvb(b'MAGCODE_DIFF_ARGS')
        # Need to be able to detect environment setting of no args ''
        if (diff_args is not None):
            return diff_args.decode()
        return settings['diff_args']
   
    def get_tail(self):
        """
        Find a tail binary
        """
        tail = os.getenvb(b'MAGCODE_TAIL')
        if (tail):
            return tail.decode()
        tail = '/bin/tail'
        if os.path.isfile(tail):
            return tail
        return '/usr/bin/tail'

    def get_tail_args(self):
        """
        Work out the tail args 
        """
        tail_args = os.getenvb(b'MAGCODE_TAIL_ARGS')
        # Need to be able to detect environment setting of no args ''
        if (tail_args is not None):
            return tail_args.decode()
        return settings['tail_args']

    def pager(self, text, file=sys.stdout):
        """
        Page through text.
        """
        if not hasattr(file, 'isatty') or not file.isatty():
            print(text, file=file)
            return os.EX_OK
        # Make sure Less is secure
        pager_env = os.environ
        if not self.admin_mode:
            pager_env.update({'LESSSECURE': '1'})
        pager_bin = self.get_pager()
        pager_args = self.get_pager_args()
        pager_argv = [pager_bin]
        if pager_args:
            pager_argv += pager_args.split()
        try:
            p1 = Popen(pager_argv, stdin=PIPE, env=pager_env)
            output = p1.communicate(input=text.encode())
        except (IOError, OSError) as exc:
            print ("Running %s failed: %s" 
                                % (pager_bin, exc.strerror),
                                file=sys.stderr)
            # This works with zone_tool as it is a mix in class
            return os.EX_SOFTWARE
        return os.EX_OK

            

