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

import sys
import os
import csv
import datetime
import locale

import facct.config as config
import facct.bill.gen_tex as gen_tex

debug = False

def load_bills(orga, year, bill_dir):
    bills = []
    year = str(year)
    year_dir = os.path.join(bill_dir, year)
    if not os.path.exists(year_dir):
        return bills
    for f in sorted(os.listdir(year_dir)):
        if not f.endswith(year + '.csv'):
            continue
        bills.append(gen_tex.Contract(orga, os.path.join(year_dir, f)))
    return bills

def get_facture_HT(dico_tmp, date, op_code, ref):
    account = 706000
    intitule = 'Prestations de service\nFacture %(client)s n°%(nb_bill)s –\
 prestations de %(month_name)s_%(year_name)s' % dico_tmp
    deb = ''
    cred = '%(income)s' % dico_tmp
    return [date, account, intitule, op_code, deb, cred, ref]

def get_VAT_account(dico_tmp, date, op_code, ref):
    account = 445710
    intitule = 'TVA collectée\nFacture %(client)s n°%(nb_bill)s – prestations\
 de %(month_name)s_%(year_name)s' % dico_tmp
    deb = ''
    cred = '%(vat)s' % dico_tmp
    return [date, account, intitule, op_code, deb, cred, ref]

def get_vente_prestation(dico_tmp, date, op_code, ref):
    account = 411000
    intitule = 'Clientes – ventes de prestations de service Facture %(client)s\
 n°%(nb_bill)s – prestations de %(month_name)s_%(year_name)s' % dico_tmp
    cred = ''
    deb = dico_tmp['include_taxe']
    return [date, account, intitule, op_code, deb, cred, ref]


def register_bill(bill):
    date = datetime.date(bill._year, bill._month, 1)
    income = bill.get_total_excluded_tax()
    vat = bill.get_VAT()
    register_date = (gen_tex.getSameDayNextMonth(date) +\
            datetime.timedelta(days=int(-1))).strftime('%Y/%m/%d')
    dico_tmp = { 'nb_bill': bill._nb_bill,
        'year_name'       : date.year,
        'month_name'      : date.strftime('%B'),
        'income'          : income,
        'vat'             : vat,
        'include_taxe'    : '%.2f' % (vat+income),
        'client'          : bill._client,
    }
    op_code = "%(client)s_M%(nb_bill)s" % dico_tmp
    ref = 'FC %(client)s %(nb_bill)s' % dico_tmp
    yield get_facture_HT(dico_tmp, register_date, op_code, ref)
    yield get_VAT_account(dico_tmp, register_date, op_code, ref)
    yield get_vente_prestation(dico_tmp, register_date, op_code, ref)

def get_operation(dico_tmp, account_name, account_nb):
    dico_tmp['account_name'] = account_name
    account_line = []
    account_line += [ dico_tmp['paid_date'].strftime('%Y/%m/%d')]
    account_line += [account_nb]
    account_line += ['%(account_name)s\nRèglement %(client)s Facture\
 n°%(nb_bill)s - prestations de %(month_name)s_%(bill_year)s'% dico_tmp]
    account_line += [
        '%(client)s_M%(nb_bill)s_%(bill_year)s paiement' % dico_tmp ]
    return account_line

def get_bank(dico_tmp):
    account_line =  get_operation(dico_tmp, 'Banque', 512100)
    account_line += ["%.3f" % dico_tmp['include_taxe']]
    account_line += [""]
    account_line += ["VIR %(client)s" % dico_tmp]
    return account_line

def get_encaissement_account(dico_tmp):
    account_line = get_operation(dico_tmp,
            'Clients- ventes de prestations de service', 411000)
    account_line += [""]
    account_line += ["%.3f" % dico_tmp['include_taxe']]
    account_line += ["VIR %(client)s" % dico_tmp]
    return account_line

def collection(orga, bill):
    date = datetime.date(bill._year, bill._month, 1)
    include_taxe = bill.get_total_tax_incl()
    paid_date = date + datetime.timedelta(days=65)
    def get_client_dico():
        return gen_tex.Client(orga, bill._client).get_dico()
    dico_tmp = { 'nb_bill': bill._nb_bill,
        'month_name'      : date.strftime('%B'),
        'bill_year'       : date.year,
        'include_taxe'    : include_taxe,
        'paid_date'       : datetime.datetime(paid_date.year, paid_date.month,
            int(get_client_dico()['pay date of month'])),
        'client'          : bill._client,
    }
    yield get_encaissement_account(dico_tmp)
    yield get_bank(dico_tmp)


def get_template(orga, bill, op, bill_dir):
    nb_days = bill.get_nb_days()
    if debug:
        print (_('contract='), bill)
        print (_('nb_days=%s') % nb_days)
    accounts = []

    date = datetime.date(bill._year, bill._month, 1)
    except_file = os.path.join(bill_dir, str(date.year), 'except.txt')
    if not os.path.exists(except_file) or\
        '%s.csv' % date.strftime('%m%Y') not in ' '.join(open(except_file)):
        if bill._month <= 12:
            for c in register_bill(bill):
                c.insert(0, op)
                accounts.append(c)
            op +=1
        else:
            sys.stderr.write(
                _('excluded: date=%(date)s, nb_days=%(nb_days)s, op=%(op)s'
                    ) % { 'date': date, 'nb_days':nb_days, 'op':op})
        advanced_date = (date + datetime.timedelta(days=65))
        if bill._year == advanced_date.year:
            for c in collection(orga, bill):
                c.insert(0, op)
                accounts.append(c)
            op +=1
    return accounts

def init_op_number(orga, year):
    account_dir = os.path.join(config.get_accounts_dir(orga), str(year))
    if not os.path.exists(account_dir):
        sys.stderr.write(_(
            'account dir "%s": no such directory!\n') % account_dir)
        sys.exit(2)

    jnl_tmpl_in = os.path.join(config.get_accounts_dir(orga),
            str(year), 'journal.ori.csv')
    jnl_tmpl_out = jnl_tmpl_in.replace('.ori.csv', '_tmpl.csv')

    op_number = 0
    if not os.path.exists(jnl_tmpl_in):
        return op_number, jnl_tmpl_out

    reader = csv.reader(open(jnl_tmpl_in, 'r'), delimiter=';', quotechar='"')
    writer = csv.writer(open(jnl_tmpl_out, 'w'), delimiter=';', quotechar='"')
    entries = set()

    for r, row in enumerate(reader):
        if r == 0:
            writer.writerow(row)
            continue
        if not row or not row[1]:
            continue
        entry = (row[1], row[4])
        if entry not in entries:
            op_number += 1
        row[0] = op_number
        writer.writerow(row)
        entries.add(entry)
    return op_number, jnl_tmpl_out

def generate_jnl(orga, year):
    op, jnl_tmpl_out = init_op_number(orga, year)
    writer = csv.writer(open(jnl_tmpl_out, 'a'), delimiter=';', quotechar='"')

    op += 1
    bill_dir = config.get_bills_dir(orga)
    for bill in load_bills(orga, year, bill_dir):
        for account in get_template(orga, bill, op, bill_dir):
            writer.writerow(account)
        op += 2

def main(orga, year):
    gen_tex.setlocale()
    if year < 1900 or year > 2100:
        sys.stderr.write(
            _('Please give a year between 1900 and 2100 (%s given)\n') % year)
        return 1

    generate_jnl(orga, year)
    return 0

if __name__ == "__main__":
    args = config.get_args(year=True)
    sys.exit(main(args.orga, args.year))
