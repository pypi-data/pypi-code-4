#!/usr/bin/python
# -*- coding: utf-8 -*-

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

import sys
import os
import csv
import glob
import calendar
import decimal

import facct.config as config
import facct.bill.gen_tex as gen_tex

def get_bill_path(orga):
    return config.get_bills_dir(orga)

def get_csv_path(orga):
    return config.get_data_dir(orga)

def get_account_path(orga):
    return config.get_accounts_dir(orga)

tables = {}
debug = False

def getNextEntry(reader):
    if 'next' in dir(reader):
        return reader.next()
    else:
        return next(reader)

def get_csv_data(orga, table_name, db_def=None, keep_first=False, csv_file_name=None,
        skip_first_col=False, start_id=0, formater=None):
    if not csv_file_name:
        csv_file_name = os.path.join(get_csv_path(orga), table_name + '.csv')

    reader = csv.reader(open(csv_file_name, 'r'), delimiter=';', quotechar='"')
    if not keep_first:
        header = getNextEntry(reader)

    csv_data = []
    first_col = 0
    if skip_first_col:
        first_col = 1
    for i, row in enumerate(reader):
        if ''.join(row).strip():
            csv_data.append([start_id+i+1]+row[first_col:])
    if formater:
        csv_data = formater(table_name, csv_data)

    if not db_def:
        db_def = get_tables()[table_name]

    NAME, TYPE = range(2)
    for i, v in enumerate(db_def):
        for r in csv_data:
            #print ('i=%s, r=%s'% (i, str(r)))
            if i>=len(r):
                sys.stderr.write (
                    'Error while loading date: r=%s i=%s for %s\n'%(
                        r, i, table_name))
                continue
            if v[TYPE] == 'INT':
                r[i] = int(r[i])
            if r[i] == '':
                r[i] = None
            if v[TYPE] == 'DATE' and r[i]:
                try:
                    if type(r[i]) == type (''):
                        r[i] = gen_tex.getDate(r[i])
                except:
                    sys.stderr.write (
                        'Error while loading date: %s %s %s\n'%(r[i], r, table_name))
    return csv_data

def set_client(orga, data):
    table_name = 'clients'
    data[table_name] = get_csv_data(orga, table_name)

def set_bankAccounts(orga, data):
    table_name = 'bank_accounts'
    data[table_name] = get_csv_data(orga, table_name)

def set_companies(orga, data):
    table_name = 'company'
    data[table_name] = get_csv_data(orga, table_name)

def set_contracts(orga, data):
    table_name = 'contracts'
    data[table_name] = get_csv_data(orga, table_name)

def set_journal_ori(orga, data):
    csv_data = []
    table_name = 'journal_ori'
    for f in glob.glob(os.path.join(
                get_account_path(orga), '20*', 'journal.ori.csv')):
        csv_data.extend(get_csv_data(orga, os.path.splitext(f)[0], tables[table_name],
         csv_file_name=f, skip_first_col=True, start_id=len(csv_data)))
    data[table_name] = csv_data
    #print(csv_data)

def set_prestation_dates(orga, data):
    table_name = 'prestation_dates'
    csv_data_tmp = []
    csv_data = []
    prestas = {}

    def retrieve_date(table_name, csv_data):
        csv_data = [w[1:] for w in csv_data]
        year, month = gen_tex.filename_info(table_name)
        all_days = []
        for v,w in zip(csv_data, calendar.Calendar().monthdatescalendar(year, month)):
            all_days.extend (zip(v,w))
        csv_data = []
        i = 1
        for d in all_days:
            if d[0] in ('1', '0.5'):
                csv_data.append ([i, d[1], float(decimal.Decimal(d[0]))])
                i += 1
        return csv_data

    for f in glob.glob(os.path.join(get_bill_path(orga), '20*', '*[0-9].csv')):
        csv_data_tmp.extend(get_csv_data(orga, os.path.splitext(f)[0],
            tables[table_name], keep_first=True,
            csv_file_name=os.path.normpath(f), formater=retrieve_date))
    for d in csv_data_tmp:
        prestas[d[1]] = d
    for i, d in enumerate(sorted(prestas.keys())):
        csv_data.append([i, prestas[d][1], prestas[d][2]])
    data[table_name] = csv_data

def get_data(orga):
    data = {}
    root_dir = config.get_value('root', orga)
    if not os.path.exists(root_dir):
        sys.stderr.write('[KO] root="%s": no such directory.\n' % root_dir)
        return data
    set_contracts(orga, data)
    set_companies(orga, data)
    set_bankAccounts(orga, data)
    set_client(orga, data)
    set_prestation_dates(orga, data)
    set_journal_ori(orga, data)
    return data

def get_tables():
    if tables:
        return tables
    tables['clients'] = [
    ('Id', 'INTEGER PRIMARY KEY'),
    ('Client', 'TEXT'),
    ('ClientName', 'TEXT'),
    ('AddressName', 'TEXT'),
    ('Street', 'TEXT'),
    ('ContractRef', 'TEXT'),
    ('payDateOfMonth', 'INT')
    ]
    tables['contracts'] = [
    ('Id', 'INTEGER PRIMARY KEY'),
    ('Client', 'TEXT'),
    ('StartDate', 'DATE'),
    ('EndDate', 'DATE'),
    ('Amount', 'INT'),
    ('Amendmend', 'TEXT'),
    ]
    tables['company'] = [
    ('Id', 'INTEGER PRIMARY KEY'),
    ('Name', 'TEXT'),
    ('Form', 'TEXT'),
    ('Capital', 'INT'),
    ('ShortAddress', 'TEXT'),
    ('SuffixAddress', 'TEXT'),
    ('Phone', 'TEXT'),
    ('Email', 'TEXT'),
    ('Siren', 'TEXT'),
    ('NIC', 'TEXT'),
    ('CodeAPE', 'TEXT'),
    ('RCS', 'TEXT'),
    ('TVACodePrefix', 'TEXT')
    ]
    tables['prestation_dates'] = [
    ('Id', 'INTEGER PRIMARY KEY'),
    ('day', 'DATE'),
    ('attendance_rate', 'DECIMAL(10)'),
    ]
    tables['journal_ori'] = [
    ('Id', 'INTEGER PRIMARY KEY'),
    ('date', 'DATE'),
    ('account', 'INT'),
    ('account_title', 'TEXT'),
    ('op_code', 'TEXT'),
    ('debit', 'NUMERIC'),
    ('credit', 'NUMERIC'),
    ('ref', 'TEXT'),
    ('unit period', 'TEXT'),
    ('value period', 'TEXT'),
    ('exception', 'TEXT'),
    ]
    tables['bank_accounts'] = [
    ('Id', 'INTEGER PRIMARY KEY'),
    ('OwnerName', 'TEXT'),
    ('BankName', 'TEXT'),
    ('Code', 'INT'),
    ('Agency', 'TEXT'),
    ('AccountNb', 'TEXT'),
    ('Key', 'INT'),
    ('BICCode', 'TEXT'),
    ('CountryCode', 'TEXT'),
    ('KeyControl', 'INT')
    ]
    return tables

def main():
    pass

if __name__ == '__main__':
    sys.exit(main())
