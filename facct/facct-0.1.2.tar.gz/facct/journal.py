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

import os
import sys
import csv
import datetime
import locale
import decimal
import glob
import re
import time
import codecs

import argparse
import config
from i18n import _
import bill.gen_tex as gen_tex

gen_tex.setlocale()
debug=False

def get_float(str):
    if str:
        return decimal.Decimal(str.replace(',', '.'))
    else:
        return decimal.Decimal(0)

def load_operations(template_file):
    reader = csv.reader(open(template_file, 'r'), delimiter=';', quotechar='"')
    op_numbers = {}
    def getNumber(ori_number):
        if ori_number not in op_numbers:
            op_numbers[ori_number] = len(op_numbers)+1
        return op_numbers[ori_number]

    for r, row in enumerate(reader):
        if row: break

    ops = {}
    for r, row in enumerate(reader):
        if not row or not row[1]:
            continue
        op_number = getNumber(row[0])
        if op_number not in ops:
            unit_period = ''
            periodicity = ''
            exception = ''
            if len(row)>9:
                unit_period = row[8]
                periodicity = row[9]
                if len(row) > 10 and row[10].strip(): exception = row[10]
            ops[op_number] = Operation(op_number, row[1],
                    unit_period, periodicity, exception)
        ops[op_number].append(row[2:8])
    return ops

def nb_bill(year, month):
    return (year - 2010) * 12 + month

def paid_nb_bill(year, month):
    return nb_bill(year, month) - 2

def paid_nb_month(year, month):
    return 1 + (paid_nb_bill(year, month) -1) % 12

def paid_month_bill(year, month):
    return datetime.date(year, paid_nb_month(year, month),1).strftime('%B')

def paid_year(year, month):
    if month < 3:
        return year - 1
    return year

class Record:
    def __init__(self, date, row):
        self.date = date
        self.row = list(row)
        _dico = {'month_name' : date.strftime('%B'),
                 'year_name' : date.year,
                 'previous_year' : date.year - 1,
                 'month_nb' : date.month,
                 'nb_bill' : nb_bill(date.year, date.month),
                 'paid_year' : paid_year(date.year, date.month),
                 'paid_nb_month' : paid_nb_month(date.year, date.month),
                 'paid_month_bill' : paid_month_bill(date.year, date.month),
                 'paid_nb_bill' : paid_nb_bill(date.year, date.month),
                 }
        for c, col in enumerate(self.row):
            self.row[c] = self.row[c] % _dico

    def __repr__(self):
        return repr((self.date, self.row))

def last_date_of_month(date):
    date_of_first_day_of_month = datetime.date(date.year, date.month, 1)
    D = date_of_first_day_of_month + datetime.timedelta(days=int(31))
    return datetime.date(D.year, D.month, 1) + datetime.timedelta(days=int(-1))

def get_day(first_date, year, month, date):
    if first_date.day > 15:
        delta_in_month = first_date.day - last_date_of_month(first_date).day
        DD = last_date_of_month(datetime.date(year, month, 1))
    else:
        delta_in_month = first_date.day - 1
        DD = datetime.date(year, month, 1)
    return (DD + datetime.timedelta(days=int(delta_in_month)))


class Operation:
    def __init__(self, op_number, first_date, unit_period,
            periodicity, exception):
        self.records = []
        self.op_number = op_number
        self.unit_period = unit_period
        self.periodicity = periodicity
        self.first_date = gen_tex.getDate(first_date)
        if not unit_period:
            unit_period = 'y'
        if not periodicity:
            periodicity = '1'
        if unit_period == 'd':
            def iter_day(date):
                return (True, date + datetime.timedelta(days=int(periodicity)) )
            self.iter_date = iter_day
        if unit_period == 'm':
            def iter_month(date):
                month = date.month + int(periodicity)
                if month < 13:
                    year = date.year
                else:
                    year = date.year+1
                    month = 1
                D = get_day(self.first_date, year, month, date)
                val = (not exception or D.month not in [
                        int(e) for e in exception.split()])
                if not val:
                    msg_err = 'exception: {0}, D.month={1}, op_number={2},'
                    msg_err += 'val={3}, D={4}\n'
                    sys.stdout.write (msg_err.format(
                                exception, D.month, op_number, val, D))
                return (val, D)
            self.iter_date = iter_month
        if unit_period == 'y':
            def iter_year(date):
                d = datetime.date(date.year + int(periodicity), date.month , 1)
                return (True, d + datetime.timedelta(days=int(date.day)))
            self.iter_date = iter_year


    def append(self, record):
        self.records.append(record)

    def gen_dates(self):
        dates = []
        tmp_date = self.first_date
        limit = datetime.date(tmp_date.year, 12, 31)
        keep = True
        while tmp_date <= limit:
            if keep:
                dates.append(tmp_date)
            (keep, tmp_date) =  self.iter_date(tmp_date)
        return dates

    def generate(self):
        records = {}
        for i, d in enumerate(self.gen_dates()):
            records[(int(self.op_number), i)] = [
                Record(d, r) for r in self.records]
        return records

(CODE, AMOUNT, DATE, LABEL, MARKED) = range(5)
def col_filter(row, cols_desc):
    l = [row[c].strip().replace(' ','') for c in cols_desc[:-1] ]
    l[AMOUNT] = l[AMOUNT].replace(',', '.')
    l[DATE] = '/'.join(l[DATE].split('/')[::-1])
    l.append( re.sub(r' +', ' ', row[cols_desc[LABEL]].strip()) )
    return l

def getDate(strDate):
    return gen_tex.getDate(strDate)

def concat_2_segments(g, f):
    max_g = getDate(g[-1][DATE])
    for i, e in enumerate(f):
        if max_g < getDate(e[DATE]):
            g.extend(f[i:])
            break
    return g

def concat_dumps(merged_dumps_list, f):
    if debug:
        print ('f=({0}, {1})'.format(getDate(f[0][DATE]), getDate(f[-1][DATE])))
    if not merged_dumps_list:
        return merged_dumps_list.append(f)

    nb = len(merged_dumps_list)
    j = nb
    min_f = getDate(f[0][DATE])
    for i,g in enumerate(merged_dumps_list):
        if min_f<getDate(g[0][DATE]):
            j=i
            break

    def max_min(a, b):
        return getDate(a[-1][DATE]) < getDate(b[0][DATE])
    if (j<nb and max_min(f, merged_dumps_list[j])) or\
            (j==nb and max_min(merged_dumps_list[nb-1], f)):
        return merged_dumps_list.insert(j, f)

    if j==nb:
        to_merge = merged_dumps_list.pop(nb-1)
        return concat_dumps(merged_dumps_list, concat_2_segments(to_merge, f))

    to_merge = merged_dumps_list.pop(j)
    return concat_dumps(merged_dumps_list, concat_2_segments(f, to_merge))

def merge_dumps(file_dumps):
    merged_dumps_list = []
    for f in file_dumps:
        if debug:
            print (len(f))
        if f:
            concat_dumps(merged_dumps_list, f)
            if debug:
                for g in merged_dumps_list:
                    print ('g=({0}, {1})'.format (
                                getDate(g[0][DATE]), getDate(g[-1][DATE])))
    bank_entries = [ ]
    for f in merged_dumps_list:
        bank_entries.extend(f)
    return bank_entries


class UnicodeReader:
    """
    A CSV reader which will iterate over lines in the CSV file "f",
        which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding='utf-8', delimiter=';'):
        self.delimiter = delimiter
        self.lines = [l for l in codecs.open(f, 'r', encoding)]

    def next(self):
        return self.__next__()

    def __next__(self):
        if not self.lines:
            return []
        return self.lines.pop(0).split(self.delimiter)

    def __iter__(self):
        return self


def loadBank(bankStatement):
    reader = UnicodeReader(bankStatement, encoding='latin1', delimiter=';')
    first_line = reader.next()

    if not first_line:
        sys.stderr.write(_('No lines in %s\n') % bankStatement)
        return None
    if not first_line[0] == 'Code Enregistrement':
        sys.stderr.write(_('%s is not a bank statement file\n') % bankStatement)
        return None

    cols_desc = []
    for title in [
        'Code Enregistrement', 'Montant', "Date d'opération", 'Libellé']:
        if sys.version_info[0] == 3:
            cols_desc.append(first_line.index(title))
        if sys.version_info[0] == 2:
            cols_desc.append(first_line.index(title.decode('utf-8')))
    lines = []
    row = reader.next()
    while row:
        l = col_filter(row, cols_desc)
        try:
            l[0] = '0%d' % int(l[0])
        except:
            pass
        if l[0] == '05':
            lines[-1][-1] += '\n' + l[-1]
        if l[0] == '04' or l[0] == '07':
            lines.append(l)
        if not lines and l[0] == '01':
            l[0] = '07'
            lines.append(l)
        row = reader.next()
    return lines

(COMPTES, INTITULE, CODE_OP, DEBIT, CREDIT) = range(5)
def skip_entries(entries, i):
    end_entries = False
    while entries[i][CODE] == '07' or entries[i][CODE] == '01':
        end_entries = (i == len(entries)-1)
        if end_entries:
            break
        i += 1
    return end_entries, i

def equiv(e_jnl, e_bk):
    found = ((e_bk[AMOUNT] == e_jnl[AMOUNT]) and (
                not e_bk[MARKED] and not e_jnl[MARKED]))
    if found:
        e_bk[MARKED] = True
        e_jnl[MARKED] = True
    return found

def checkRightInLeft(left_entries, right_entries):
    j=0
    i=0
    while i < len(left_entries) and j < len(right_entries):
        end_entries, i = skip_entries(left_entries, i)
        if end_entries:
            break
        end_entries, j = skip_entries(right_entries, j)
        if end_entries:
            break

        e_left = left_entries[i]
        e_right = right_entries[j]
        max_range = getDate(e_right[DATE]) + datetime.timedelta(days=int(10))
        min_range = getDate(e_right[DATE]) - datetime.timedelta(days=int(10))
        date_jnl = getDate(e_left[DATE])

        i_sav = i
        while date_jnl<=max_range:
            if date_jnl>= min_range and equiv(e_left, e_right):
                break
            i += 1
            end_entries, i = skip_entries(left_entries, i)
            if end_entries:
                break
            e_left = left_entries[i]
            date_jnl = getDate(e_left[DATE])
        if i>i_sav:
            i = i_sav+1
        j += 1

def get_valid_jnl_slice(bank_entries, jnl_entries):
    if not  bank_entries:
        return []
    for bk_begin in bank_entries:
        if not bk_begin[CODE] == '07':
            break
    if bk_begin[CODE] == '07':
        return []
    for bk_end in bank_entries[::-1]:
        if not bk_end[CODE] == '07':
            break

    for j_begin, je in enumerate(jnl_entries):
        if getDate(je[DATE]) >= getDate(bk_begin[DATE]):
            break
    for j_end, je in enumerate(jnl_entries):
        if getDate(je[DATE]) > getDate(bk_end[DATE]):
            break
    return jnl_entries[j_begin:j_end]

class WriteGenerator:
    def __init__(self, year, bank_entries):
        self._bank_entries = bank_entries
        self._year = year
        self._rows = []
        self._orphelins = []
        for e in self._bank_entries:
            e[LABEL] = ' '.join(e[LABEL].split('\n')[0].split()[1:-1])

    def compute(self):
        essence = ( 'Essence',
                ('625000', 'Voyage et déplacement'),
                ('401100', 'Fournisseurs - Achats de biens et services'),
                ('512100', 'Banque'))
        peage = ('Péage', essence[1], essence[2], essence[3])
        categories = {
            peage: ('COFIROUTE',),
            essence: ('PAREA CONFL DAC', 'PAREA CONFL STA', 'REL. CLAIR BOIS',
                'STATION BP ROC', 'COFIROUTE', 'E.LECLERC DAC', 'ESSO PAVE'),
        }
        self._rows = []
        def get_row(cat, entry, transit_account=True, bill_time='facture'):
            label, date = entry[LABEL], entry[DATE]
            account, deb, cred = 2, '', '%s' % abs(e[AMOUNT])
            if bill_time == 'facture' and not transit_account:
                account, deb, cred = 1, cred, deb
            if bill_time == 'paiement' and transit_account:
                deb, cred = cred, deb
            if bill_time == 'paiement' and not transit_account:
                account = 3
            return [cat[account][0], '%s\n%s - %s' %(cat[account][1], cat[0],
                    str(label)), '%s %s %s'%(cat[0], str(date), bill_time),
                    deb, cred, '' ]

        for e in self._bank_entries:
            ops = []
            for cat in sorted(categories.keys(), reverse=True):
                if ( e[LABEL] in categories[cat]):
                    d = getDate(e[DATE])
                    ops.append( Record(d, get_row(cat, e, False, 'facture')))
                    ops.append( Record(d, get_row(cat, e, True, 'facture')))
                    ops.append( Record(d, get_row(cat, e, True, 'paiement')))
                    ops.append( Record(d, get_row(cat, e, False, 'paiement')))
                    break
            self._rows.extend(ops)
            if not ops:
                self._orphelins.append(e)
                print (e)

def get_account_dir(orga):
    return config.get_accounts_dir(orga)

class Journal:
    def __init__(self, orga, year):
        self.orga = orga
        self.year = year
        self.entries = []
        self.ops = {}

    def add(self, records):
        self.ops.update(records)

    def get_account_dir(self):
        return os.path.join(get_account_dir(self.orga), str(self.year))

    def sort(self):
        self.entries.sort(key=lambda record: record.date)

    def merge(self):
        for k in sorted(self.ops.keys()):
           self.entries.extend(self.ops[k])

    def cleanup(self):
        self.merge()
        tmp = {}
        for e in reversed(self.entries):
            k = e.row[COMPTES]+e.row[CODE_OP]
            if k in tmp:
                e.row.append('DUPLICATE')
            tmp[k] = e
        self.entries = [e for e in self.entries if not e.row[-1] == 'DUPLICATE']
        self.sort()

    def corpTaxWritting(self, tax):
        r1 = Record(datetime.date(self.year, 12, 31),
                ['695000', 'Impôts sur les bénéfices\nEstimation',
                'IS_%s' % self.year, '%s' % tax, '', "Ecriture d'inventaire"])
        r2 = Record(datetime.date(self.year, 12, 31),
                ['448600', 'Etat-Charges à payer',
                'IS_%s' % self.year, '', '%s' % tax, "Ecriture d'inventaire"])
        self.entries.append(r1)
        self.entries.append(r2)

    def profitCalculation(self):
        gross_profit = 0
        for e in self.entries:
            account = int(e.row[COMPTES])
            if account == 695000:
                continue
            if (account >= 600000 and account < 700000) or account == 706000:
                gross_profit += get_float(e.row[CREDIT]) - get_float(e.row[DEBIT])
        return gross_profit

    def corpTaxCalculation(self, gross_profit):
        tax = 0
        SS_ceiling = 38120
        if gross_profit>=0:
            tax = gross_profit*15/100
        if gross_profit>=SS_ceiling:
            tax += (gross_profit-SS_ceiling)/3
        return decimal.Decimal( '%.2f' % round(tax,2))

    def computCorpTax(self):
        gross_profit = self.profitCalculation()
        tax = self.corpTaxCalculation(gross_profit)
        self.corpTaxWritting(tax)

    def register(self):
        file_name = os.path.join(self.get_account_dir(), '%s.csv' % self.year)
        writer = csv.writer(open(file_name, 'w'), delimiter=',', quotechar='"')
        header = ['N°', 'Date', 'Comptes', 'Intitulé', 'Code opération',
             'Débit', 'Crédit', 'Réf. Pièce']
        writer.writerow(header)
        for i, e in enumerate(self.entries):
            e.row.insert(0, e.date.strftime('%Y/%m/%d'))
            e.row.insert(0, i+1)
            writer.writerow(e.row)

    def load_operations(self, file_name):
        operations = load_operations(file_name)
        for op in operations.values():
            self.add(op.generate())

    def compareStartingTotal(self, bank_entries):
        self.bankInJnl = [ {'Date': e.date.strftime('%Y/%m/%d'),
            'Débit': e.row[DEBIT], 'Crédit': e.row[CREDIT],
            'Code opération': e.row[CODE_OP]}
            for e in self.entries if e.row[COMPTES] == '512100']
        if not bank_entries or not self.bankInJnl:
            return
        be = bank_entries[0]
        if not be[CODE] == '07':
            return
        je = self.bankInJnl[0]
        date_min = getDate(be[DATE])
        if getDate(je['Date'])> date_min:
            sys.stderr.write(_(
                'Please check bank journal entries between {0}-01-01 and {1}\n'
                    ).format(date_min.year, date_min))
            sys.stderr.write(_('Total should be {0} on {1}\n').format(
                        be[AMOUNT], date_min))
            sys.exit(2)

        i=0
        while getDate(je['Date'])< date_min:
            i += 1
            je = self.bankInJnl[i]

        j = 0
        total = 0
        log = []
        while getDate(self.bankInJnl[j]['Date']) <= \
            getDate(self.bankInJnl[i]['Date']):
            je = self.bankInJnl[j]
            deb = get_float(je['Débit'])
            cred = get_float(je['Crédit'])
            total += deb - cred
            log.append([je['Date'], total, deb, cred])
            j += 1

        if not (float(be[AMOUNT])-float(total)):
            sys.stdout.write(_(
                '[OK] Total is {0} in bank and is {1} in journal on {2}.\n'
                ).format( be[AMOUNT], total, date_min))
            return
        for l in log:
            sys.stderr.write('%s\n' % l)
        sys.stderr.write(_(
            'Please check bank journal entries between {0}-01-01 and {1}\n'
                ).format(date_min.year, date_min))
        sys.stderr.write(_(
            'Total should be {0} on {1} and is in journal {2} at this time.\n'
                ).format (be[AMOUNT], date_min, total))
        sys.exit(2)

    def compareTotals(self, bank_entries):
        self.bankInJnl = [ {'Date': e.date.strftime('%Y/%m/%d'),
            'Débit': e.row[DEBIT], 'Crédit': e.row[CREDIT],
            'Code opération': e.row[CODE_OP]}
            for e in self.entries if e.row[COMPTES] == '512100']
        if not bank_entries or not self.bankInJnl:
            return
        be = bank_entries[0]
        if not be[CODE] == '07':
            return
        je = self.bankInJnl[0]
        date_min = getDate(be[DATE])
        b=0
        j = 0
        log = []
        total = 0
        while b < len(bank_entries):
            be = bank_entries[b]
            date_min = getDate(be[DATE])
            while j<len(self.bankInJnl) and\
                getDate(self.bankInJnl[j]['Date'])<=date_min:
                je = self.bankInJnl[j]
                deb = get_float(je['Débit'])
                cred = get_float(je['Crédit'])
                date = je['Date']
                total += deb - cred
                if float(be[AMOUNT])-float(total):
                    log.append([je, be, total])
                j += 1
            b += 1

        if not log:
            return
        sys.stdout.write(_(
        '[OK] The last same total is {0} in bank ({1}) and in journal ({2}).\n'
            ).format( log[-1][1][AMOUNT], log[-1][1][DATE], log[-1][0]['Date']))

    def compareResult(self, bank_entries, jnl_slide):
        self.bank = [ list(e.values()) for e in bank_entries\
                    if not e[MARKED] and e[CODE] == '04' and e[AMOUNT]]
        self.jnl = [ list(e.values()) for e in jnl_slide\
                   if not e[MARKED] and e[CODE] == '04' and e[AMOUNT]]

    def generateFromstatements(self):
        if self.jnl:
            for e in self.jnl:
                sys.stdout.write ('Jnl:%s\n'% str(e))
            for e in self.bank:
                sys.stdout.write ('Bnk:%s\n'% str(e))
            # We do not generate content if Jnl not clean, so we return
            return
        if self.bank:
            wGen = WriteGenerator(self.year, self.bank)
            wGen.compute()
            self.entries.extend(wGen._rows)
            self.sort()

    def checkBank(self):
        pattern = os.path.join(self.get_account_dir(), 'hsbc','*hsbc*.csv')
        bank_entries = merge_dumps([loadBank(f) for f in glob.glob(pattern)])
        if debug:
            print (len(bank_entries))
        if bank_entries:
            print (_('HSBC statements loaded.'))
        self.compareStartingTotal(bank_entries)

        bank_entries = [{DATE:e[DATE],AMOUNT: get_float(e[AMOUNT]),
            CODE: e[CODE], MARKED:False, LABEL:e[LABEL]} for e in bank_entries]
        jnl_entries = [{DATE:e['Date'],
            AMOUNT:get_float(e['Débit'])-get_float(e['Crédit']), CODE: '04',
            LABEL: e['Code opération'], MARKED:False} for e in self.bankInJnl]
        bank_entries = sorted(bank_entries, key=lambda e: (
                    getDate(e[DATE]), int(e[CODE]), e[AMOUNT]))
        jnl_entries = sorted(jnl_entries, key=lambda e: (
                    getDate(e[DATE]), e[AMOUNT]))

        checkRightInLeft(jnl_entries, bank_entries)
        jnl_slide = get_valid_jnl_slice(bank_entries, jnl_entries)
        checkRightInLeft(bank_entries, jnl_slide)
        self.compareResult(bank_entries, jnl_slide)
        self.generateFromstatements()
        self.compareTotals([e for e in bank_entries if e[CODE]=='07'])

def main(orga, year):
    if int(year) < 2010:
        sys.stderr.write(_('Please give a year after 2010 (%s given)\n') % year)
        return 2
    journal = Journal(orga, year)
    tmpl_file = os.path.join(get_account_dir(orga),
            str(year), 'journal_tmpl.csv')
    journal.load_operations(tmpl_file)
    journal.cleanup()
    journal.checkBank()
    journal.computCorpTax()
    journal.register()
    return 0

if __name__ == "__main__":
    args = config.get_args(year=True)
    sys.exit(main(args.orga, args.year))
