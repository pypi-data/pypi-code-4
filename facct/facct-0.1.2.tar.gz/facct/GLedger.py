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
import decimal
import datetime
import platform

import facct.config as config
from facct.i18n import _

def get_float(str):
    if not str: return decimal.Decimal(0)
    if not type(str) == type(''): return str
    return decimal.Decimal(str.replace(',', '.'))

debug = False
epsilon = 0

class VAT:
    DUE_MONTH = (4, 7, 10, 12)
    DUE_DAY = 21
    def __init__(self, accounts):
        self._accounts = accounts
        self._debug = False

    def get_date(self, e):
        D = e['Date'].split('/')[:]
        return datetime.date(int(D[0]), int(D[1]), int(D[2]))

    def same_period(self, date, current_year, month_index):
        return date < datetime.date(
                current_year, VAT.DUE_MONTH[month_index], VAT.DUE_DAY)

    def account_balance(self, account_nb, limit_date = datetime.date.today()):
        current_year = limit_date.year
        diff =  0
        if account_nb not in self._accounts:
            return diff
        for e in self._accounts[account_nb]:
            date = self.get_date(e)
            if date > limit_date:
                break

            diff -= get_float(e['Débit'])
            diff += get_float(e['Crédit'])
        return diff

    def get_limit_date(self):
        today = datetime.date.today()
        for month in VAT.DUE_MONTH:
            due_date = datetime.date(today.year, month, VAT.DUE_DAY)
            if due_date > today:
                return due_date
        return due_date

    def unpaid(self, operation_code):
        for e in self._accounts[512100]:
            if e['Code opération'] == operation_code:
                if self._debug:
                    print (_('Paid :%s') % operation_code)
                return False
        if self._debug:
            print (_('Unpaid %s') % operation_code)
        return True

    def vat_from_unpaid_bill(self):
        account_nb = 445710
        limit_date = datetime.date.today()
        current_year = limit_date.year
        diff =  0
        if account_nb not in self._accounts:
            return diff
        for e in self._accounts[account_nb]:
            date = self.get_date(e)
            if date > limit_date:
                break

            if self.unpaid(e['Code opération']):
                diff -= get_float(e['Débit'])
                diff += get_float(e['Crédit'])
        return diff

    def comput(self):
        today = datetime.date.today()
        due_date = self.get_limit_date()
        diff = self.account_balance(445710) + self.account_balance(445660)
        diff -= self.vat_from_unpaid_bill()
        need_to_register = (today + datetime.timedelta(days=15) > due_date)
        enough = (diff > 1000) or (diff < -150)

        side = _('restitution')
        if diff >0:
            side = _('payment')
        tva_info = (side, diff, due_date.strftime('%Y/%m/%d'))
        txt_info = _('The next {0} VAT : {1} on {2}.').format(*tva_info)
        if not need_to_register or enough:
            print (txt_info)
        else:
            print (txt_info + _(' is not enough at this time'))

def set_float(nb):
    nb = str(nb).replace('.', ',')
    if nb.isdigit():
        return nb + ',000'
    else:
        return nb

class Journal:
    def __init__(self, csv_file):
        self._csv_file = csv_file

    def load_entries(self):
        reader = csv.reader(open(self._csv_file, 'r'),
                delimiter=',', quotechar='"')
        header_list = []
        for row in reader:
            if not row:
                continue
            if row[0] == 'N°':
                header_list = row
                break
        if not header_list:
            sys.stderr.write(_('No header found!\n'))
            sys.exit(2)

        entries = []
        self._accounts = {}
        for row in reader:
            if row:
                if platform.os == 'nt':
                    row = [x.encode('utf-8') for x in row]
                entries.append(dict(zip(header_list, row)))
                account = entries[-1]['Comptes']
                account_number = int(account)
                if account_number not in self._accounts:
                    self._accounts[account_number] = []
                self._accounts[account_number].append(entries[-1])
        return self.check_entries(entries)

    def check_entries(self, entries):
        self._debt_sum = 0
        self._credit_sum = 0
        total_solde = 0
        last_item = ''
        debug = False
        for entry in entries:
            current_item = entry['N°']
            debit = get_float(entry['Débit'])
            credit = get_float(entry['Crédit'])
            self._debt_sum += debit
            self._credit_sum += credit
            total_solde += (debit - credit)
            if debug:
                print("%s total_debit = %s"  % (current_item, self._debt_sum))
                print("%s total_credit = %s" % (current_item, self._credit_sum))
                print("%s total_solde = %s"  % (current_item, total_solde))
            if (abs(total_solde) <= decimal.Decimal(epsilon) ):
                last_item = current_item
                if debug:
                    last_entry = entry
                    print ("last_item: %s" % last_item)
                    print ("last_entry: %s" % str(last_entry))
        status = (last_item == entries[-1]['N°'])
        if not status:
            txt = _('inconsistency entries last_item={0}, last nb entry={1}\n')
            sys.stderr.write (txt.format(last_item, entries[-1]['N°']))
            if last_item:
                for e in entries:
                    if int(e['N°']) == int(last_item)+1:
                        print (_('starting point of incorrect chain:\n%s'
                                    ) % str(e))
                sys.stderr.write (_(
                    'The last correct state was for entry %s\n') % last_item)
            sys.exit(2)
        return status

class balance_account:
    def __init__(self, id, name, title, debit, credit, solde_deb, solde_cred):
        self._id = id
        self._name = name
        self._title = title
        self._debit = debit
        self._credit = credit
        self._solde_debit = solde_deb
        self._solde_credit = solde_cred
    def write(self, writer):
        writer.writerow(['', '', str(self._id), self._name, self._title,
                set_float(self._debit), set_float(self._credit),
                set_float(self._solde_debit), set_float(self._solde_credit)])
    def display(self):
        sys.stdout.write( self._id)
        sys.stdout.write( self._name)
        sys.stdout.write( self._title)
        sys.stdout.write( self._debit)
        sys.stdout.write( self._credit)
        sys.stdout.write( self._solde_debit)
        sys.stdout.write( self._solde_credit)


DEBIT, CREDIT = range(2)
class BalanceSheet:
    def __init__(self, balance):
        self._bal = balance

    def load_and_save_year(self):
        def getGoodSide(a, side1, side2):
            account = self._bal.read_bal_account(a)
            val = getNum(account[side1]) - getNum(account[side2])
            if val>0:
                return val
            return 0

        def getNum(val):
            if val == '':
                return 0
            return val

        def deb(a):
            return getGoodSide(a, DEBIT, CREDIT)

        def cred(a):
            return getGoodSide(a, CREDIT, DEBIT)

        assets = [
            ("Immobilisations incorporelles:", 0),
            ("- Fonds commercial", 0),
            ("- Autres", 0),
            ("Immobilisations corporelles:", 0),
            ("Immobilisations financières:", 0),
            ["TOTAL : Actif immobilisé (I)", 0],
            ("Stock en cours (autres que marchandises)", 0),
            ("Marchandises", 0),
            ("Avances et accomptes verses sur commandes", 0),
            ("Créances: clients et accomptes ratachés", deb(411000)),
            ("Créances: autres", sum([deb(x) for x in [421000, 428600, 431000,
                                     437010, 437020, 445660, 445710, 445810,
                                     448600, 457000]] )),
            ("Valeurs mobilières de placement", 0),
            ("Disponibilités (autres que caisse)", sum([deb(x) for x in [
                                                       512100, 512101 ]] )),
            ("Caisse", 0),
            ["TOTAL : Actif circulant (II)", 0],
            ("Charges constatées d'avance (III)", deb(486000) + deb(438000)),
            ["TOTAL GENERAL:  I + II +III", 0]
            ]
        assets[5][1] = sum(c[1] for c in assets[:4])
        assets[14][1] = sum(c[1] for c in assets[5:14])
        assets[16][1] = sum(assets[l][1] for l in [5, 14, 15])
        liabilities = [
            ("Capital", cred(101000)),
            ("Ecarts de réévaluation", 0),
            ("Réserves: réserve légale", cred(106100)),
            ("Réserves: réserves réglementées", 0),
            ("Réserves: Autres", 0),
            ("Report à nouveau", cred(110000)-deb(110000)-deb(120000)),
            ("Résultat de l'exercice", self._bal.net_profit),
            ("Provision réglementée", 0),
            ["TOTAL : Capitaux propres (I)", 0],
            ("Provisions (II)", 0),
            ("Dettes: emprunts et dettes assimilées",
             cred(513000)+cred(512100)),
            ("Dettes: avances et acomptes reçus sur\nCommandes en cours", 0),
            ("Dettes: Fournisseurs et comptes ratachés", cred(401100)),
            ("Dettes: Autres", sum([cred(x) for x in [411000, 421000, 428600,
                                   431000, 437010, 437020, 445660, 445710,
                                   445810, 448600, 438000, 457000]])),
            ["TOTAL :  Dettes (III)", 0],
            ("Produits constatés d'avance (IV)", 0),
            ["TOTAL GENERAL:  I + II +III + IV", 0],
            ]
        liabilities[8][1] = sum(c[1] for c in liabilities[:8])
        liabilities[14][1] = sum(c[1] for c in liabilities[10:14])
        liabilities[16][1] = sum(liabilities[l][1] for l in [8, 9, 14, 15])
        self._liabilities = liabilities
        self._assets = assets
        if len(assets) != len(liabilities):
            sys.stderr.write(_(
                    'assets and liabilities number lines are different!\n'))
            sys.exit(2)
        txt_info = _('Balance sheet: assets and liabilities totals are')
        if abs(assets[-1][1] - liabilities[-1][1]) > decimal.Decimal(epsilon):
            sys.stderr.write(_(
                '{0} different! assets={1}, liabilities={2}\n').format(
                        txt_info, assets[-1][1], liabilities[-1][1]))
        else:
            sys.stdout.write(_('%s equal!\n') % txt_info)

    def get_file_name(self, year=None):
        if not year:
            year = self._bal._year
        return os.path.join( config.get_accounts_dir(self._bal._orga),
                '%s' % year, 'balance_sheet_%s.csv' % year)

    def load_previous_year(self):
        file_balance_sheet = self.get_file_name(self._bal._year - 1)
        self.prev_bal_sheet = []
        if os.path.exists(file_balance_sheet):
            reader = csv.reader(open(file_balance_sheet, 'r'),
                    delimiter=',', quotechar='"')
            for row in reader:
                self.prev_bal_sheet.append(dict(zip( ['actif_name',
                    'growth_actif', 'amortization', 'actif_val', 'prev_actif',
                    'passif_name', 'passif_val', 'prev_passif'], row)))

    def get_prev_year(self, line, column):
        if not self.prev_bal_sheet or line >= len(self.prev_bal_sheet):
            return ''
        return self.prev_bal_sheet[line][column]

    def write_csv(self):
        writer = csv.writer(
                open(self.get_file_name(), 'w'), delimiter=',', quotechar='"')
        for i in range(len(self._assets)):
            groth = '%.2f' % round(self._assets[i][1],2)
            writer.writerow([ self._assets[i][0], groth, '', groth,
                self.get_prev_year(i, 'actif_val'), self._liabilities[i][0],
                '%.2f' % round(self._liabilities[i][1],2),
                self.get_prev_year(i, 'passif_val')])

class IncomeStatement:
    def __init__(self, balance):
        self._bal = balance

    def load_and_save_year(self):
        def deb(a):
            if not self._bal.read_bal_account(a)[CREDIT] and\
                not self._bal.read_bal_account(a)[DEBIT]:
                return 0
            if self._bal.read_bal_account(a)[DEBIT]:
                return self._bal.read_bal_account(a)[DEBIT]
            else:
                return - self._bal.read_bal_account(a)[CREDIT]

        def cred(a):
            return self._bal.read_bal_account(a)[CREDIT]

        def getProfit(value):
            if value>0:
                return abs(value)
            else:
                return 0
        def getLoss(value):
            if value<0:
                return abs(value)
            else:
                return 0
        external_expenses = [
                616400, 618000, 618300, 622700, 625000, 626000, 627000]
        charges = [("Charges d'exploitation :\nAchat de marchandises", 0),
        ("Variation de stocks (marchandises)", 0),
        ("Achats d'approvisionnements", deb(606400)),
        ("Variations de stocks (approvisionnements)", 0),
        ("Autres charges externes", sum([deb(x) for x in external_expenses])),
        ("Impôts, taxes et versements assimilés", deb(635110)),
        ("Rémunérations du personnel", deb(644000)),
        ("Charges sociales", sum([deb(x) for x in [645100, 645300, 645800]])),
        ("Dotations aux amortissements", 0),
        ("Dotations aux provisions", 0),
        ("Autres charges", 0),
        ("Charges financières", deb(627800)),
        ["Total I", 0],
        ("Charges exceptionnelles (II)", 0),
        ("Impôts sur les bénéfices (III)", deb(695000)),
        ["Total des charges (I +II+ III)", 0],
        ("Solde créditeur : bénéfice (I)", getProfit(self._bal.net_profit)),
        ["TOTAL GENERAL", 0]]
        charges[12][1] = sum(c[1] for c in charges[:12])
        charges[15][1] = sum(c[1] for c in charges[12:15])
        charges[17][1] = sum(c[1] for c in charges[15:17])

        income = [("Produits d'exploitation :\nVentes de marchandises", 0),
        ("Production vendue (biens et services)", cred(706000)),
        ("Production stockée", 0),
        ("Production immobilisée", 0),
        ("Subventions d'exploitation", 0),
        ("Autres produits", 0),
        ("Produits financiers", 0),
        ["Total I", 0],
        ("dont à l’exploitation :", 0),
        ("Produits exceptionnels (II)", 0),
        ["Total des produits (I+II)", 0],
        ("Solde débiteur : perte", getLoss(self._bal.net_profit)),
        ["TOTAL GENERAL", 0],
        ('', 0),
        ('', 0),
        ('', 0),
        ('', 0),
        ('', 0), ]
        income[7][1] = sum(c[1] for c in income[:7])
        income[10][1] = sum(c[1] for c in income[7:10])
        income[12][1] = sum(c[1] for c in income[10:12])

        self._charges = charges
        self._produits = income
        if len(charges) != len(income):
            sys.stderr.write(_(
                        'charges and income number lines are different!\n'))
            sys.exit(2)
        txt_info = _('Income statement: charges and income totals are')
        if abs(charges[-1][1] - income[12][1]) > decimal.Decimal(epsilon):
            sys.stderr.write(_('{0} different! charges={1}, income={2}\n'
                        ).format(txt_info, charges[-1][1], income[12][1]))
            sys.exit(2)
        else:
            sys.stdout.write(_('%s are equal!\n') % txt_info)

    def get_file_name(self, year=None):
        if not year:
            year = self._bal._year
        return os.path.join( config.get_accounts_dir(self._bal._orga),
                '%s' % year, 'IncomeStatement_%s.csv' % year)

    def load_previous_year(self):
        file_income_statement = self.get_file_name(self._bal._year - 1)
        self.prev_income_stat = []
        if os.path.exists(file_income_statement):
            reader = csv.reader(open(file_income_statement, 'r'),
                    delimiter=',', quotechar='"')
            for row in reader:
                self.prev_income_stat.append(dict(zip([ 'charges_name',
                    'charges_val', 'prev_charges', 'produits_name',
                    'produits_val', 'prev_produits'], row)))

    def get_prev_year(self, line, column):
        if not self.prev_income_stat or line >= len(self.prev_income_stat):
            return ''
        return self.prev_income_stat[line][column]

    def write_csv(self):
        writer = csv.writer(open(self.get_file_name(), 'w'),
                delimiter=',', quotechar='"')
        for i in range(len(self._charges)):
            writer.writerow([self._charges[i][0],
                '%.2f' % round(self._charges[i][1],2),
                self.get_prev_year(i, 'charges_val'), self._produits[i][0],
                '%.2f' % round(self._produits[i][1],2),
                self.get_prev_year(i, 'produits_val')])

TOT_DEBT, TOT_CRED, TOT_SOLD_DEBT, TOT_SOLD_CRED = range(4)
class Balance:
    def __init__(self, orga, year):
        self._bal_accounts = []
        self._orga = orga
        self._year = year

    def register_account(self, account):
        self._bal_accounts.append(account)

    def set_writer(self, writer):
        self._writer = writer

    def write_partial_balance(self, account_range):
        summary = [0, 0, 0, 0]
        for account in self._bal_accounts :
            if ((account._name >= account_range[0] * 100000) and\
                    (account._name < (account_range[-1]+1) *100000)):
                account.write(self._writer)
                summary[TOT_DEBT] += account._debit
                summary[TOT_CRED] += account._credit
                summary[TOT_SOLD_DEBT] += get_float(account._solde_debit)
                summary[TOT_SOLD_CRED] += get_float(account._solde_credit)
        self._writer.writerow(['', 'Totaux des classes %s à %s' % (
            account_range[0], account_range[-1]), '', '', '',
            set_float(summary[TOT_DEBT]), set_float(summary[TOT_CRED]),
            set_float(summary[TOT_SOLD_DEBT]),
            set_float(summary[TOT_SOLD_CRED])])
        return summary

    def write(self):
        self._writer.writerow(['', '', 'N°', 'Compte', 'Intitulé du compte',
                'Total débit', 'Total crédit', 'Solde débit', 'Solde crédit'])
        bilan = self.write_partial_balance((1,5))
        c_exploitation = self.write_partial_balance((6,7))
        sum_bal = []
        for i in range(4):
            sum_bal.append(c_exploitation[i] + bilan[i])
        self._debt_sum = sum_bal[TOT_DEBT]
        self._credit_sum = sum_bal[TOT_CRED]
        self._writer.writerow(['', '', '', '', '', set_float(self._debt_sum),
            set_float(self._credit_sum), set_float(sum_bal[TOT_SOLD_DEBT]),
            set_float(sum_bal[TOT_SOLD_CRED])])
        text_info = _('Balance {0} balanced! debit={1}, credit={2}\n')
        if (abs(self._debt_sum-self._credit_sum) > decimal.Decimal(epsilon) ):
            sys.stderr.write( text_info.format(
                        'is not ', self._debt_sum, self._credit_sum))
            sys.exit(2)
        if debug:
            sys.stdout.write( text_info.format(
                    'is', self._debt_sum, self._credit_sum))

    def compare_with_journal(self, jnl):
        (jd, jc, bd, bc) = (jnl._debt_sum, jnl._credit_sum,
                self._debt_sum, self._credit_sum)
        if debug:
            print ("jnl: total_debit = %s"  % (jd))
            print ("jnl: total_credit = %s" % (jc))
            print ("bal: total_debit = %s"  % (bd))
            print ("bal: total_credit = %s" % (bc))
        def get_totals(deb, cred):
            return ['', set_float(deb), set_float(cred),
                '', set_float(deb-cred)]
        for l in [[], ['', 'Comparaison Totaux balance et Journal:',
            '', '', '', 'Débit', 'Crédit'],
            ['', '', '', 'Balance'] + get_totals(bd, bc),
            ['', '', '', 'Journal'] + get_totals(jd, jc),
            ['', '', '', ''] + get_totals(bd-jd, bc-jc) ]:
            self._writer.writerow(l)

    def profitCalculation(self):
        gross_profit = 0
        for a in  self._bal_accounts:
            account = a._name
            if account == 695000:
                continue
            if (account >= 600000 and account < 700000) or account == 706000:
                gross_profit += get_float(a._solde_credit) -\
                                get_float(a._solde_debit)
        return gross_profit

    def corpTaxCalculation(self, gross_profit):
        tax = 0
        SS_ceiling = 38120
        if gross_profit>=0:
            tax = gross_profit*15/100
        if gross_profit>=SS_ceiling:
            tax += (gross_profit-SS_ceiling)/3
        return decimal.Decimal(str(round(tax,2)))

    def check_for_exercice_result(self):
        if 120000 not in [x._name for x in self._bal_accounts]:
            val = self.net_profit
            self.register_account(balance_account( len(self._bal_accounts),
                        120000, "Résultat de l'exercice", val, val, '', ''))

    def computCorpTax(self):
        gross_profit = self.profitCalculation()
        tax = self.corpTaxCalculation(gross_profit)

        self.gross_profit = gross_profit
        self.tax = tax
        self.net_profit = gross_profit - tax
        self.check_for_exercice_result()

    def get_account(self, account):
        for a in  self._bal_accounts:
            if a._name == account:
                return a
        return None

    def read_bal_account(self, account):
        for a in  self._bal_accounts:
            if a._name == account:
                return a._solde_debit, a._solde_credit
        return 0, 0

    def print_compagny_taxes(self):
        self._writer.writerow([])
        self._writer.writerow(['', '', '', '',
                'Bénéfices avant impôts sur IS:', round(self.gross_profit,2)])
        self._writer.writerow(['', '', '', '',
                'IS', '%.2f' % round(self.tax,2)])
        self._writer.writerow(['', '', '', '',
                'Bénéfice distribuable', round(self.net_profit,2)])

    def comput_SIG(self):
        CA = self.read_bal_account(706000)[CREDIT]
        trade_marging = CA
        production_and_service = 0
        VA = trade_marging + production_and_service
        for a in [ 606400, 616400, 618000, 618300, 622700, 625000 ]:
            if self.read_bal_account(a)[DEBIT]:
                VA -= self.read_bal_account(a)[DEBIT]
            else:
                if (self.read_bal_account(a)[CREDIT]):
                    VA += self.read_bal_account(a)[CREDIT]

        EBE = VA
        for a in [ 635110, 644000, 645100, 645300, 645800 ]:
            EBE -= self.read_bal_account(a)[DEBIT]

        RE = EBE
        RF = 0
        RCAI = RE + RF
        Rexcept = 0
        if debug:
            sys.stderr.write(
            'RCAI=%s, Rexcept=%s, self.read_bal_account(695000)[DEBIT]=%s\n' % (
                RCAI , Rexcept , (self.read_bal_account(695000)[DEBIT] )))
        if self.read_bal_account(695000)[DEBIT]:
            RN = RCAI + Rexcept - (self.read_bal_account(695000)[DEBIT] + 0)
        else:
            RN = RCAI + Rexcept

        slots = ('Production de l\'exercice', 'Marge commerciale',
                'Consommations de l\'exercice en provenance de tiers')
        SIG = [
        ('Chiffre d\'affaire', CA),
        ("""Marge commerciale= 
 Ventes de marchandises et de services -
 Coût d'achat des marchandises vendues""", trade_marging),
        ('''Production de l\'exercice= \nProduction vendue +
  Production immobilisée +/-\n  Production stockée''',
                production_and_service),
        ('Valeur Ajoutée (VA) =\n %s +\n %s -\n %s' % slots, VA),
        ("""Exedent brut d'exploitation (EBE) =
 VA + Subventions d'exploitations -
 Charges du personnel -
 Impôts, taxes et versements assimilés""", EBE),
        ("""Résultat d'exploitation =
 EBE + Autre produit d'exploitation -
 Autre charge d'exploitation +
 Transfert de charge d'exploitation -
 Dotation aux ammortissements et provisions d'exploitations""", RE),
        ("""Résultat financier =
 Produits financiers – Chrages financières""", RF),
        ("""Résultat courant avant impôt (RCAI) =
 Résultat d'exploitation + Résultat financier""", RCAI),
        ("""Résultat exceptionnel =
 Produits exceptionnels – Charges exceptionnelles""", Rexcept),
        ("""Résultat net de l'excercice =
 RCAI + Résultat exceptionnel -
 Impôt sur les bénéfices – Participation salariale""", RN),
        ]
        self._writer.writerow([])
        self._writer.writerow(['', '', '', '',
                'Tableau des soldes intermédiares de gestion (SIG):'])
        for l in SIG:
            self._writer.writerow(['', '', '', '', l[0], l[1]])

    def social_taxes(self):
        SS_ceiling = decimal.Decimal(38120)
        SN = decimal.Decimal(self.read_bal_account(644000)[DEBIT])
        base_calcul = 9 * SN /10
        RSI_1 = min(base_calcul, SS_ceiling) * 65 /1000
        RSI_2 = max(base_calcul - SS_ceiling, decimal.Decimal(0)) * 59 /1000
        RSI = RSI_1 + RSI_2
        URSSAF = base_calcul * 54 /1000
        URSSAF_form_pro = SS_ceiling * 15 /10000
        CIPAV_1 = min(base_calcul, SS_ceiling*85/100)*86/1000
        CIPAV_2 = max(decimal.Decimal(0),
                base_calcul-decimal.Decimal(SS_ceiling*85/100))*16/1000
        CIPAV = CIPAV_1 + CIPAV_2
        if base_calcul<40605:
            VIEILL = 988
        else:
            VIEILL = 2064
        DECE = 76
        CIPAV_TOT = CIPAV + VIEILL + DECE

        social_addback = ( 2000*(RSI+CIPAV_TOT) +\
                base_calcul*108 + SS_ceiling*3 + SN*8*9*2) / (23*40*2)
        base_calcul_CSR = SN * 9 /10 + social_addback
        CSG_CRDS_ND = base_calcul_CSR * 29 /1000
        CSG = base_calcul_CSR * 51 /1000
        CSG_CRDS = CSG_CRDS_ND + CSG
        URSSAF_TOT = URSSAF + URSSAF_form_pro + CSG_CRDS
        SN_TO_DECLARE = SN + CSG_CRDS_ND
        partCS_out = decimal.Decimal(0)
        if SN:
            partCS_out = social_addback / SN
        partCS_in = social_addback / (SN + social_addback)
        RB = base_calcul + social_addback
        social_addback = RSI + URSSAF_TOT + CIPAV_TOT
        if not round(social_addback,2) == round(RSI + URSSAF_TOT + CIPAV_TOT,2):
            sys.stderr.write(_('Error while computing social_addback\n'))
            sys.exit(2)

        social = [('',''),
        ("Plafond sécurité sociale", SS_ceiling),
        ("Salaire net", SN),
        ("Charge sociale à réintégrer", social_addback),
        ('',''),
        ("Base de calcul (90% de salaire net)", base_calcul),
        ("RSI tranche 1 (6,5% plafond SS)", RSI_1),
        ("RSI tranche 2 (5,9% au dessus plafond SS)", RSI_2),
        ("RSI total (assurance maladie)", RSI),
        ('',''),
        ("Base de calcul (90% salaire net + charges réintégrées)",
         base_calcul_CSR),
        ("CSG + CRDS non déductibles (2,9%)", CSG_CRDS_ND),
        ("CSG +  déductibles (5,1%)", CSG),
        ("CSG+ CRDS", CSG_CRDS),
        ("Allocation familialle: base de calcul (90% salaire net)",
         base_calcul),
        ("URSSAF (5,4%)", URSSAF),
        ("URSSAF (formation pro.)", URSSAF_form_pro),
        ("URSSAF: TOTAL", URSSAF_TOT),
        ('',''),
        ("Salaire net à déclarer", SN_TO_DECLARE),
        ('',''),
        ("CIPAV: base de calcul (90% de salaire net)", base_calcul),
        ("CIPAV: vieillesse de base 8,6% tranche 1", CIPAV_1),
        ("CIPAV: vieillesse de base 1,6% tranche 2", CIPAV_2),
        ("CIPAV: vieillesse de base", CIPAV),
        ("CIPAV: vieillesse complémentaire  si < 40605: 988 sinon 2064",
         VIEILL),
        ("CIPAV: invalidité décès (classe A: 76)", DECE),
        ("CIPAV: TOTAL", CIPAV_TOT),
        ('',''),
        ("Total charges sociales",  social_addback),
        ("Cotisations obligatoires", social_addback - CSG_CRDS),
        ("Portion charge en dehors du salaire", partCS_out),
        ("Portion charge en dedans (salaire net + charges)", partCS_in),
        ("Revenu brut (charges + 90% salaire net)", RB) ]
        for l in social:
            if l[1]:
                val = '%.2f' % round(l[1], 2)
            else:
                val = l[1]
            self._writer.writerow(['', '', '', '', l[0], val])

    def merge_vat(self, account_number, deb, cred):
        if account_number == 445660:
            deb = 0
            cred = 0
        if account_number == 445710:
           deb_vat_deductible = self.read_bal_account(445660)[DEBIT]
           cred_vat_deductible = self.read_bal_account(445660)[CREDIT]
           if deb_vat_deductible:
               deb = get_float(str(deb)) + get_float(str(deb_vat_deductible))
           if cred_vat_deductible:
               cred = get_float(str(cred)) + get_float(str(cred_vat_deductible))
        return deb, cred

    def get_result(self):
        if self.net_profit>=0:
            deb =  ''
            cred = round(self.net_profit,3)
            title = "Résultat de l'exercice (bénéfice)"
        else:
            deb = - round(self.net_profit,3)
            cred = ''
            title = "Résultat de l'exercice (déficit)"
        if debug:
            print ('self.net_profit=%s' % self.net_profit)
            print ('deb=%s' % deb)
            print ('cred=%s' % cred)
        return deb, cred, title

    def open_entries_of_next_year(self):
        for l in [ [], [], [],
            ['', "Ecriture d'ouverture pour %s:" %(self._year + 1)],
            ['', 'N°', 'Date', 'Comptes', 'Intitulé',
                'Code opération', 'Débit', 'Crédit', 'Réf. Pièce']]:
            self._writer.writerow(l)
        RESULTAT = 0

        account_numbers  = list([a._name for a in self._bal_accounts\
                if (a._name<600000)])
        account_numbers.sort()
        tot_debit = 0
        tot_credit = 0
        def disp(val):
            if val:
                return '%.2f' % val
            return val
        for i, account_number in enumerate(account_numbers):
            if account_number == 120000:
                deb, cred, title = self.get_result()
            else:
                deb = self.read_bal_account(account_number)[DEBIT]
                cred = self.read_bal_account(account_number)[CREDIT]
                title = self.get_account(account_number)._title.strip('\n')
            if account_number == 445660 or account_number == 445710:
                deb, cred = self.merge_vat(account_number, deb, cred)
            if deb:
                tot_debit += get_float(str(deb))
            if cred:
                tot_credit += get_float(str(cred))
            if debug:
                print ('i=%s, deb=%s, cred=%s' % (i, deb, cred))
            if deb or cred:
                date = datetime.date(self._year+1, 1, 1).strftime('%Y/%m/%d')
                self._writer.writerow(['', i+1, date,
                    account_number, title, 'OUVERTURE %s' % (self._year + 1),
                    disp(deb), disp(cred), 'BILAN %s' % self._year])
        if abs(tot_credit - tot_debit)>decimal.Decimal(epsilon):
            txt = _('New year opening error ({0}):\n' + \
                    'tot_debit={1} differs from tot_credit={2} !!\n\n')
            sys.stderr.write(txt.format(self._year+1, tot_debit, tot_credit))
            sys.exit(2)

    def income_statement(self):
        cr = IncomeStatement(self)
        cr.load_and_save_year()
        cr.load_previous_year()
        cr.write_csv()

    def balance_sheet(self):
        bs = BalanceSheet(self)
        bs.load_and_save_year()
        bs.load_previous_year()
        bs.write_csv()

def get_title(PC, c):
    id_sav = ''
    c_id = int(c)
    for id_str in sorted(PC.keys()):
        if c_id >= int(id_str + '0' * (6-len(id_str))):
            id_sav = id_str
        elif id_sav:
            return PC[id_sav]
    return ''

def diff_sides(debit, credit):
    debt = ''
    cred = ''
    val = abs(debit - credit)
    if debit > credit:
        debt = val
    if credit > debit:
        cred = val
    return debt, cred

def get_script_dir():
    return os.path.dirname(__file__)

def write_GLedger(orga, year,journal_file, accounts):
    ledger_file = journal_file.split('.')[0] + '.gl.csv'
    writer = csv.writer(open(ledger_file, 'w'), delimiter=',', quotechar='"')
    columns = ['N°', 'Date', 'Comptes', 'Intitulé', 'Code opération',
    'Débit', 'Crédit' ]
    balance = Balance (orga, year)
    balance.set_writer(writer)

    # Get plan comptable
    plan_comptable_file = os.path.join(config.get_internal_data_dir(),
            'plan_comptable.txt')
    if not os.path.exists(plan_comptable_file):
        sys.stderr.write(_('%s: not found\n') % plan_comptable_file)
        sys.exit(2)
    PC = {}
    for C in open(plan_comptable_file):
        dico = C.split(':')
        PC[dico[0]] = dico[1].strip('\n')

    tot_debit = 0
    tot_credit = 0
    for i, c in enumerate(sorted(accounts.keys())):
        account_debit = 0
        account_credit = 0
        writer.writerow([''] + columns)
        for entry in accounts[c]:
            account_debit += get_float(entry['Débit'])
            account_credit += get_float(entry['Crédit'])
            writer.writerow([''] + [entry[col] for col in columns ] + [
                    set_float(account_debit), set_float(account_credit)])
        tot_debit += account_debit
        tot_credit += account_credit
        title = get_title(PC, c)
        writer.writerow(['Totaux', '', str(i+1), c, title, '', ] + [
                set_float(account_debit), set_float(account_credit)])
        writer.writerow([])
        debt, cred = diff_sides(account_debit, account_credit)
        balance.register_account(balance_account(
                    i+1, c, title, account_debit, account_credit, debt, cred))

    if (abs(tot_credit-tot_debit) > decimal.Decimal(epsilon) ):
        sys.stderr.write(_('Journal is not balanced! debit={0}, credit={1}\n'
                    ).format(tot_debit, tot_credit))
        sys.exit(2)
    else:
        if debug:
            sys.stdout.write(_('Journal is balanced! debit={0}, credit={1}\n'
                        ).format(tot_debit, tot_credit))
    return balance

def main(orga, year):
    journal_file = os.path.abspath( os.path.join(
                config.get_accounts_dir(orga), '%s'%year, '%s.csv'%year ))
    if not os.path.exists(journal_file):
        sys.stderr.write(_(
                journal_file + "not found, cannot generate General Ledger\n"))
        sys.exit(2)

    jnl = Journal(journal_file)
    if not jnl.load_entries():
        return 2

    balance = write_GLedger(orga, year, journal_file, jnl._accounts)
    balance.computCorpTax()
    balance.write()
    VAT(jnl._accounts).comput()

    # 1 Need to compare balance and journal
    #   Write comparison
    balance.compare_with_journal(jnl)

    # 2 Comput IS
    #   Write IS
    #   Write distributable profit
    balance.print_compagny_taxes()

    # 3 Comput intermediate balance of gestion (SIG)
    #   Write SIG
    balance.comput_SIG()

    # 4 Comput social taxes
    #   Write social taxes
    balance.social_taxes()

    # 5 Comput Open entries for the next year (OENT)
    #   Write OENT
    balance.open_entries_of_next_year()

    # 6 Comput Income Statement
    #   Write Income Statement
    balance.income_statement()

    # 7 Comput Balance Sheet
    #   Write Balance Sheet
    balance.balance_sheet()

    return 0

if __name__ == "__main__":
    args = config.get_args(year=True)
    sys.exit(main(args.orga, args.year))
