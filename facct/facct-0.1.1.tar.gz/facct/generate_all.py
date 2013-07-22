#!/usr/bin/python
import os
import sys
import config
import grand_livre
import override_tmpl_jnl as over_jnl
import journal
from i18n import _

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
    if 0 != grand_livre.main(orga, year):
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
