# -*- coding: utf-8 -*-
#   Copyright (C) 2009, 2010 Rocky Bernstein <rocky@gnu.org>
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
#    02110-1301 USA.

from import_relative import *
# Our local modules

Mbase_subcmd = import_relative('base_subcmd', '..', 'pydbgr')
Mcmdfns      = import_relative('cmdfns', '...', 'pydbgr')

class SetListSize(Mbase_subcmd.DebuggerSubcommand):
    "Set the number lines printed in a *list* command by default"
    
    in_list    = True
    min_abbrev = len('lis') # Need at least "set lis"

    def run(self, args):
        Mcmdfns.run_set_int(self, ' '.join(args),
                            "The 'listsize' command requires a line count.", 
                            0, None)
        return
    pass


