#!/usr/bin/python
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

import csv
import os
import sys
import datetime
import shutil

import generate_all
import config
from i18n import _

def account_dir(orga, year):
    return os.path.join(config.get_accounts_dir(orga), '%s' % year)

def get_ori_file(orga, year):
    return os.path.join(account_dir(orga, year), 'journal.ori.csv')

def get_ledger_file(orga, year):
    return os.path.join(account_dir(orga, year), '%s.gl.csv' % year)

def generate_ori(orga, year):
    writer_ori = csv.writer(open(get_ori_file(orga, year), 'w'),
            delimiter=';', quotechar='"')

    if not os.path.exists(account_dir(orga, year-1)):
        first_line = ['Code op type', 'First date', 'Comptes', 'Intitulé',
        'Code opération', 'Débit', 'Crédit', 'Réf. Pièce',
        'Period unite <y,m,d>', 'Period value', '[opt]: exception']
        writer_ori.writerow(first_line)
        return

    prev_jnl_ori = get_ori_file(orga, year-1)
    if not os.path.exists(prev_jnl_ori):
        sys.stderr.write(_('%s: file not found\n') % prev_jnl_ori)
        sys.exit(2)
    prev_gnl_ledger = get_ledger_file(orga, year-1)
    if not os.path.exists(prev_gnl_ledger):
        sys.stderr.write(_('%s: file not found\n') % prev_gnl_ledger)
        sys.exit(2)

    reader_ori = csv.reader(open(prev_jnl_ori, 'r'), delimiter=';', quotechar='"')
    reader_gl = csv.reader(open(prev_gnl_ledger, 'r'), quotechar='"')

    for row in reader_ori:
        if len(row)<2:
            continue
        if row[1] == datetime.date(year-1, 1, 1).strftime('%Y/%m/%d'):
            continue
        if row[4] == 'AFFECTATION DIV IN':
            continue
        row = [ v.replace(str(year), str(year+1)) for v in row]
        row = [ v.replace(str(year-1), str(year)) for v in row]
        row = [ v.replace(str(year-2), str(year-1)) for v in row]
        writer_ori.writerow(row)

    profit = (0, 0)
    for row in reader_gl:
        if not row:
            continue
        if len(row)<=5:
            continue
        if 'OUVERTURE %s' % year in row[5]:
            writer_ori.writerow(row[1:])
            if 'Résultat de l\'exercice' in row[4]:
                profit = (row[6], row[7])

    res = 'bénéfice'
    if profit[0]:
        res = 'déficit'
    date = datetime.date(year, 3, 7).strftime('%Y/%m/%d')
    row1 = ['',date, 120000,  "Résultat de l'exercice (%s)" % res,
    'AFFECTATION DEFICIT IN', profit[1], profit[0],
    'PV approbation des comptes %s'%(year-1), 'y', '1', None]
    row2 = ['',date, 110000, "Report à nouveau %(year_name)s",
        'AFFECTATION DEFICIT IN', profit[0], profit[1],
        'PV approbation des comptes %s'%(year-1), 'y', '1', None]
    writer_ori.writerow(row1)
    writer_ori.writerow(row2)

def check_first_run(orga, year, create):
    root = config.get_value('root', orga)
    if not root:
        if not create:
            sys.stderr.write(_('config root="%s" not defined\n') % root)
        if not config.initialize(orga):
            sys.exit(2)
        root = config.get_value('root', orga)
    if os.path.exists(root):
        return account_dir(orga, year)
    os.makedirs(config.get_bills_dir(orga))
    os.makedirs(config.get_accounts_dir(orga))
    os.makedirs(config.get_data_dir(orga))
    for file_name in ['contracts', 'company', 'clients', 'bank_accounts']:
        src = os.path.join(config.get_internal_data_dir(),
                'templates', '%s.csv' % file_name)
        dest = os.path.join(config.get_data_dir(orga), file_name)
        shutil.copy(src, config.get_data_dir(orga))
        sys.stdout.write(_('You will have to modify dummy %s.csv\n') % dest)
    return account_dir(orga, year)

def main(orga, year, create):
    if create:
        config.add(orga)
    year_dir = account_dir(orga, year)
    if os.path.exists(year_dir):
        return _('%s: already exists\n') % year_dir
    year_dir = check_first_run(orga, year, create)
    if os.path.exists(year_dir):
        return _('%s: already exists\n') % year_dir
    os.makedirs(year_dir)
    for dir_name in ['declaration_IS', 'gerance', 'hsbc',
        'organismes_sociaux', 'tribunal_commerce']:
        os.makedirs(os.path.join(year_dir, dir_name))

    generate_ori(orga, year)
    generate_all.main(orga, account_dir(orga, year))

if __name__ == "__main__":
    args = config.get_args(year=True, create=True)
    sys.exit(main(args.orga, args.year, args.create))

