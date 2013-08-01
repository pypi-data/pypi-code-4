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
import calendar
import decimal
import shutil
import subprocess
import locale
import re
import glob
import datetime
import platform
import facct.config as config
from facct.i18n import _

def setlocale():
    local_name = 'fr_FR.UTF-8'
    if platform.os.name == 'nt':
       #See: http://msdn.microsoft.com/en-us/library/cdax410z%28VS.71%29.aspx
       local_name = 'fra_fra'
       if 'fr_fr' in locale.locale_alias:
           locale.setlocale(locale.LC_ALL, local_name)
    else:
        if local_name.split('.')[0].lower() in locale.locale_alias:
            locale.setlocale(locale.LC_ALL, local_name)
setlocale()


def get_float(str):
    if str:
        if str == '-':
            return 0
        return decimal.Decimal(str.replace(',', '.'))
    else:
        return decimal.Decimal(0)

def filename_info(csv_file_name):
    base_name = os.path.basename(csv_file_name).split('.')[0]
    if len(base_name)<6:
        sys.stderr.write(_('No correct input file name (eg. 012011.csv)\n'))
        sys.exit(2)
    month = int(''.join(base_name[0:2]))
    year = int(''.join(base_name[2:]))
    return year, month

def next_entry(reader):
    for r in reader: return r
    return []

def load_entries(csv_file_name):
    reader = csv.reader(open(csv_file_name, 'r'), delimiter=';', quotechar='"')
    dico_prestation = {}
    year, month = filename_info(csv_file_name)
    for week in calendar.monthcalendar(year, month):
        r = next_entry(reader)
        dico_prestation.update(zip(week, r))
    return year, month, dico_prestation

def check_output(p):
    if p.stderr:
        if p.stdout:
            print (''.join(p.stdout))
        print (''.join(p.stderr))
    return (0 == p.returncode)

def gen_dvi(dico):
    if not os.path.exists(dico['root_file'] + '.tex'):
        sys.stderr.write(_('%(root_file)s.tex: file not found\n') % dico)
        sys.exit(2)
        return False
    p = subprocess.Popen('latex -version', shell=True, stdout=subprocess.PIPE)
    p.communicate()
    if p.returncode:
        sys.stderr.write(_('latex command not found, please install' +\
            ' (MikTeX on Windows, texlive-latex on Linux)\n'))
        return False
    p = subprocess.Popen('latex -halt-on-error %(base_file)s.tex' % dico,
        cwd=dico['tmp_dir'], shell=True, stdout=subprocess.PIPE)
    p.communicate()
    rc = check_output(p)
    if p.stdout:
        p.stdout.close()
    if not rc:
        log_file = dico['root_file'] + '.log'
        if os.path.exists(log_file):
            for l in open(log_file):
                print (l)
        sys.exit(2)
    print (_('%(base_file)s.dvi generated.') % dico)
    return True

def gen_pdf(dico):
    if not os.path.exists(dico['root_file']+'.dvi'):
        sys.stderr.write(_('%(root_file)s.dvi: file not found\n') % dico)
        sys.exit(2)
        return False
    pdf_file = os.path.join('%(year_dir)s', '%(base_file)s.pdf')
    if platform.os.name == 'nt':
        cmd = 'dvipdfm %(root_file)s.dvi -o ' + pdf_file
    else:
        cmd = 'dvipdf %(root_file)s.dvi ' + pdf_file
    p = subprocess.Popen( cmd % dico, shell=True, stdout=subprocess.PIPE)

    p.communicate()
    rc = check_output(p)
    p.stdout.close()
    if not rc:
        sys.stderr.write(_('Fatal error while generating PDF file %s.') % (
                    pdf_file % dico))
        sys.exit(2)
    print (_('%(base_file)s.pdf generated.') % dico)

def write_pdf(orga, year, month, company_name, unicode_TeX):
    year_dir = os.path.join(get_db_path(orga), str(year))
    tmp_dir = os.path.join(get_db_path(orga), 'tmp')
    dico = { 'year_dir':year_dir,
        'id_bill' : '0'*(2-len(str(month))) + '%d%d' % (month, year),
        'company_name' : company_name,
        'tmp_dir' : tmp_dir,
    }
    dico['bill_parameters'] = 'data_%(id_bill)s' % dico
    dico['base_file'] = 'Facture_%(id_bill)s_%(company_name)s' % dico
    dico['bill_tmpl'] = 'Facture_GEN_company_client'
    dico['root_file'] = os.path.join(dico['tmp_dir'], dico['base_file'])
    TeX_bill = '''
    \\include{%(bill_parameters)s}
    \\include{%(bill_tmpl)s}''' % dico

    if not os.path.isdir(tmp_dir):
        os.mkdir(tmp_dir)
    if not os.path.isdir(year_dir):
        os.mkdir(year_dir)

    parameters_file = os.path.join(tmp_dir, '%(bill_parameters)s.tex' % dico)
    open(parameters_file, 'w').write(unicode_TeX)
    open(os.path.join(tmp_dir, '%(base_file)s.tex' % dico), 'w').write(TeX_bill)
    print (_('%(base_file)s.tex generated.') % dico)

    tmpl_file = os.path.join(config.get_internal_data_dir(),
            '%(bill_tmpl)s.tex' % dico)
    if not os.path.exists(tmpl_file):
        sys.stderr.write(_('%s: file not found\n') % tmpl_file)
        sys.exit(2)
    shutil.copy(tmpl_file, tmp_dir)

    if gen_dvi(dico):
        gen_pdf(dico)

    for f in glob.glob(os.path.join(tmp_dir, '*')):
        os.remove(f)

def getDate(val):
    import time
    return datetime.datetime(*(time.strptime(val, '%Y/%m/%d')[0:6])).date()

def getSameDayNextMonth(date):
    return datetime.date(date.year + date.month//12,
            (date.month % 12) + 1, date.day)

def get_db_path(orga):
    return  config.get_bills_dir(orga)

def get_reader(orga, csv_file_name):
    csv_file = os.path.join(config.get_data_dir(orga), csv_file_name)
    if not os.path.exists(csv_file):
        sys.stderr.write(_('%s does not exist\n') % csv_file)
        sys.exit(2)
    return csv.reader(open(csv_file, 'r'), delimiter=';', quotechar='"')

class Contract:
    def __init__(self, orga, csv_file_name):
        year, month, dico_prestation = load_entries(csv_file_name)
        self._orga = orga
        self._year = year
        self._month = month
        self._client = None
        self._day_price = []
        self._dico_prestation = dico_prestation
        self._contracts = {}
        self.load()
        self.getDaysByAmendment()
        self._total_excluded_tax = None

    def __str__(self):
        return '''
_year = %(year)s
_month = %(month)s
_client = %(client)s
_day_price = %(day_price)s
_amendment = %(amendment)s
_nb_bill = %(nb_bill)s
''' % { 'year' : self._year,
        'month' : self._month,
        'client' : self._client,
        'day_price' : self._day_price,
        'amendment' : self._amendment,
        'nb_bill' : self._nb_bill }

    def getClient(self):
        CLIENT, START_TIME, STOP_TIME, AMOUNT, AMENDMENT = range(5)
        T_start = datetime.date(self._year, self._month, 1)
        T_stop = getSameDayNextMonth(T_start) + datetime.timedelta(days=int(-1))
        max_time = None
        min_time = None
        for c in sorted(self._contracts.keys()):
            row = self._contracts[c]
            TR_start = getDate(row[START_TIME])
            TR_stop = None
            if row[STOP_TIME]:
                TR_stop = getDate(row[STOP_TIME])
            if (TR_start <= T_stop and (not TR_stop or TR_stop >= T_start)) or\
                     (TR_start >= T_start and (TR_stop and TR_stop <= T_stop)):
                if not max_time or TR_start > max_time:
                    max_time = TR_start
                    self._client = row[CLIENT]
                    self._amendment = row[AMENDMENT]
                    val = [TR_start, int(row[AMOUNT])]
                    if min_time == None or TR_start < min_time:
                        self._day_price.insert(0, val)
                        min_time = TR_start
                    else:
                        self._day_price.append(val)
        if False:
            print ('self.client=%s'%self._client)
            print ('self.day_price=%s'%self._day_price)
            print ('self.amendment=%s'%self._amendment)

    def getBillNb(self):
        CLIENT, START_TIME, STOP_TIME, AMOUNT, AMENDMENT = range(5)
        min_time = None
        for c in sorted(self._contracts.keys()):
            row = self._contracts[c]
            row_start_time = getDate(row[START_TIME])
            row_stop_time = None
            if row[STOP_TIME]:
                row_stop_time = getDate(row[STOP_TIME])
            if not row[CLIENT] == self._client:
                continue
            if min_time == None or row_start_time < min_time:
                min_time = row_start_time
        self._nb_bill = 0
        if min_time:
            self._nb_bill = (self._year - min_time.year) * 12 +\
                           self._month - min_time.month + 1

    def load(self):
        CLIENT, START_TIME, STOP_TIME, AMOUNT, AMENDMENT = range(5)
        reader = get_reader(self._orga, 'contracts.csv')
        for row in reader:
            if not row or row[0] == 'client':
                continue
            self._contracts[getDate(row[START_TIME])] = row
        self.getClient()
        self.getBillNb()

    def set_nbDays(self, day_index, nb_contract):
        day = datetime.date(self._year, self._month, 1) +\
              datetime.timedelta(days=day_index)
        if nb_contract+1 < len(self._day_price):
            if day > self._day_price[nb_contract+1][0]:
                nb_contract += 1
        val = decimal.Decimal(self._dico_prestation[day_index])
        if not self._day_price:
            return 0
        if len(self._day_price[nb_contract]) == 2:
            self._day_price[nb_contract].append(val)
        else:
            self._day_price[nb_contract][2] += val
        return nb_contract

    def getDaysByAmendment(self):
        nb_contract = 0
        for week in calendar.monthcalendar(self._year, self._month):
            for d in week:
                if self._dico_prestation[d] in ('1', '0.5'):
                    nb_contract = self.set_nbDays(d, nb_contract)

    def get_calculus(self):
        sep=''
        if len(self._day_price) == 1:
            sep=' '
        return '+'.join ([
            '%s%s*%s%s' % (tjm[2],sep,sep,tjm[1]) for tjm in self._day_price])

    def get_nb_days(self):
        return sum ([ tjm[2] for tjm in self._day_price])

    def get_total_excluded_tax(self):
        if not self._total_excluded_tax:
            self._total_excluded_tax = sum (
                    [ tjm[1]*tjm[2] for tjm in self._day_price])
        return self._total_excluded_tax

    def get_VAT(self):
        if not self._total_excluded_tax:
            self._total_excluded_tax = self.get_total_excluded_tax()
        return decimal.Decimal('%.3f' % round(
                    self._total_excluded_tax * decimal.Decimal(0.196), 2))

    def get_total_tax_incl(self):
        if not self._total_excluded_tax:
            self._total_excluded_tax = self.get_total_excluded_tax()
        return round(self._total_excluded_tax + self.get_VAT(),2)

    def get_dico(bill):
        return { 'year' : bill._year,
            'month name': get_month_name(bill._year, bill._month),
            'month id'  : '0'*(2-len(str(bill._month))) + str(bill._month),
            'last day'  : sorted(bill._dico_prestation.keys())[-1],
            'nb days'   : bill.get_nb_days(),
            'nb bill'   : '0'*(6-len(str(bill._nb_bill))) +str(bill._nb_bill),
            'total VAT' : bill.get_total_excluded_tax(),
            'VAT'       : '%.2f' % bill.get_VAT(),
            'total'     : '%.2f' % bill.get_total_tax_incl(),
            'calculus'  : bill.get_calculus(),
            'amendment' : bill._amendment,
        }

    def get_name(self):
        return 'bill'

def get_encoding():
    if platform.system().split('-')[0] in ('Windows', 'CYGWIN_NT'):
        return 'windows-1252'
    return 'utf-8'

class TeX:
    def __init__(self):
        pass
    def calendar(self, bill):
        tex_weeks = ''
        for week in calendar.monthcalendar(bill._year, bill._month):
            tex_weeks += '\\semaine '
            for d in week:
                tex_weeks += '{{'
                if bill._dico_prestation[d] == '0.5':
                    tex_weeks += '%s (1/2)' % str(d)
                    tex_weeks += '}{'
                    tex_weeks += '*'
                if bill._dico_prestation[d] == '1':
                    tex_weeks += str(d)
                    tex_weeks += '}{'
                    tex_weeks += '*'
                if bill._dico_prestation[d] == '0':
                    tex_weeks += str(d)
                    tex_weeks += '}{'
                    tex_weeks += '\\ '
                if bill._dico_prestation[d] == '-':
                    tex_weeks += '~'
                    tex_weeks += '}{'
                    tex_weeks += '~'
                tex_weeks += '}}'
            tex_weeks += '%\n'
        return '''\\newcommand{\\tableau}{%%\n%(tex_weeks)s\n} ''' % {
            'tex_weeks' : tex_weeks}

    def getVarDef(self, db):
        def getVarDef_fromVal(k, v):
            return r'\gdef\%s%s{%s}' % (db.get_name(),
                    ''.join([w[0].upper()+w[1:] for w in k.split()]),
                    str(v).replace('_','\_'))
        return '\n'.join([
                getVarDef_fromVal(k, v) for k,v in db.get_dico().items()])

    def create_utf8_translation_table(self):
        tr_table = {}
        utf8_file = os.path.join(config.get_internal_data_dir(), 'utf8ienc.dtx')
        for line in open(utf8_file):
            m = re.match(r'%.*\DeclareUnicodeCharacter\{(\w+)\}\{(.*)\}', line)
            if m:
                codepoint, latex = m.groups()
                latex = latex.replace('@tabacckludge', '')
                tr_table[int(codepoint, 16)] = decode(latex)
        return tr_table

    def get_unicode_TeX(self, tex_data, dir_root):
        tr_table = self.create_utf8_translation_table()
        if sys.version_info[0] >= 3:
            return tex_data.translate(tr_table)
        return decode(tex_data).translate(tr_table).encode(get_encoding())


def decode(s):
    if sys.version_info[0] >= 3:
        return s
    return s.decode(get_encoding())

def get_month_name(year, month):
    month_name = datetime.date(year, month, 1).strftime('%B')
    month_name = month_name[0].upper() + month_name[1:]
    return month_name

def bill_creation(orga, bill, company, dir_root):
    tex = TeX()
    db_list = [ Client(orga, bill._client), bill, company, Bank(orga)]
    return tex.get_unicode_TeX(
        '\n'.join([tex.calendar(bill)]+[tex.getVarDef(db) for db in db_list]),
        dir_root)

def init_bill(orga, csv_file_name):
    year, month = filename_info(csv_file_name)
    year_bill_dir = os.path.join(config.get_bills_dir(orga), str(year))
    if not os.path.exists(year_bill_dir):
        os.makedirs(year_bill_dir)
    def deco(day_of_week, day_of_month):
        if not day_of_month:
            return '-'
        if day_of_week%7 > 4:
            return '0'
        return '1'

    lines = []
    for w in calendar.monthcalendar(year, month):
        lines.append(';'.join([ deco(dw, dm) for dw, dm in enumerate(w)]) +'\n')
    csv_file_name = os.path.join(year_bill_dir, os.path.basename(csv_file_name))
    open(csv_file_name, 'a').writelines(lines)
    return csv_file_name

class Company():
    def __init__(self, orga):
        reader = get_reader(orga, 'company.csv')
        header = next_entry(reader)
        self._dico = {}
        for r in reader:
            self._dico.update(zip(header, r))
            long_form = None
            if self._dico['form'] == 'SARL':
                long_form = 'Société à Responsabilité Limitée'
            VAT_intra = self._dico['VAT code prefix'] + self._dico['Siren'].strip()
            capital = locale.format('%d', int(self._dico['capital']),
                    grouping=True)
            self._dico.update({
                'intracommunautary VAT' : VAT_intra,
                'compact siren' : ''.join(self._dico['Siren'].split()),
                'capital' : capital, 'Company long form' : long_form, })
            break; #We select just the first company name

    def get_name(self):
        return 'company'

    def get_dico(self):
        return self._dico

    def __getitem__(self, k):
        return self._dico[k]

class Bank():
    def __init__(self, orga):
        reader = get_reader(orga, 'bank_accounts.csv')
        header = next_entry(reader)
        self._dico = {}
        for r in reader:
            self._dico.update(zip(header, r))
            iban = ''.join(self._dico[h] for h in [
                    'code', 'agency', 'account number', 'key'])
            IBAN = ' '.join( [ iban[4*i:4*(i+1)]
                        for i in range(len(iban)//4 + len(iban)%4)])
            self._dico.update({ 'IBAN' : IBAN,
                    'short account number' : self._dico['account number'][:5]})
            break; #We select just the first bank

    def get_name(self):
        return 'bank'

    def get_dico(self):
        return self._dico

    def __getitem__(self, k):
        return self._dico[k]

class Client():
    def __init__(self, orga, client_name):
        reader = get_reader(orga, 'clients.csv')
        header = next_entry(reader)
        client_info = []
        for row in reader:
            if row[0] == client_name:
                client_info = row
                break
        if not client_info:
            sys.stderr.write(_('Client {0} not found in {1}\n').format(
                        client_name, 'clients.csv'))
            sys.exit(2)
        self._dico = {}
        self._dico.update(zip(header, client_info))

    def get_name(self):
        return 'client'

    def get_dico(self):
        return self._dico

def main(orga, csv_file_name):
    root_dir = config.get_value('root', orga)
    if not os.path.exists(root_dir):
        sys.stderr.write(_(
            'config root:"%s" no such directory, please check!\n') % root_dir)
        return 2

    if not os.path.isfile(csv_file_name):
        csv_file_name = init_bill(orga, csv_file_name)

    bill = Contract(orga, csv_file_name)
    company = Company(orga)
    dir_root = os.path.dirname(csv_file_name)
    tex_data = bill_creation(orga, bill, company, dir_root)
    write_pdf(orga, bill._year, bill._month, company['Name'], tex_data)

if __name__ == '__main__':
    args = config.get_args(bill_name=True)
    sys.exit(main(args.orga, args.bill_name))
