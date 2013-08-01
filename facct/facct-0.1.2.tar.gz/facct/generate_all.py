#!/usr/bin/env python
#-*- coding: utf-8 -*-

# Copyright (c) 2013 Eric F <efigue> Figerson
# Author(s):
#   Eric F <eric.foss@free.fr>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import sys
import facct.config as config
import facct.GLedger as GLedger
import facct.override_tmpl_jnl as over_jnl
import facct.journal as journal
from facct.i18n import _

def override_template(orga, year):
    print (_('Overriding journal template...'))
    if 0 != over_jnl.main(orga, year):
        sys.stderr.write(_('Error while overrriding journal template.\n'))
        sys.exit(2)

def get_journal(orga, year):
    print (_('Generating journal...'))
    if 0 != journal.main(orga, year):
        sys.stderr.write(_('Error while generating journal !\n'))
        sys.exit(2)

def general_ledger(orga, year):
    print (_('Generating general ledger...'))
    if 0 != GLedger.main(orga, year):
        sys.stderr.write(_('Error while generating general ledger !\n'))
        sys.exit(2)

def main(orga, account_dir):
    year = int(os.path.basename(account_dir))
    override_template(orga, year)
    get_journal(orga, year)
    general_ledger(orga, year)

    print (_('Everything was generated correctly for %s!!') % year)
    return 0

if __name__ == "__main__":
    args = config.get_args()
    account_dir = args.account_dir
    if not account_dir:
        account_dir = config.get_accounts_dir()
    if not os.path.exists(account_dir):
        sys.stderr.write(_('%s: directory not found\n') % account_dir)
        sys.exit(2)
    sys.exit(main(args.orga, os.path.abspath(account_dir)))
