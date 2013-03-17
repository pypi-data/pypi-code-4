# -*- coding: UTF-8 -*-
## Copyright 2012 Luc Saffre
## This file is part of the Lino project.
## Lino is free software; you can redistribute it and/or modify 
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 3 of the License, or
## (at your option) any later version.
## Lino is distributed in the hope that it will be useful, 
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the 
## GNU General Public License for more details.
## You should have received a copy of the GNU General Public License
## along with Lino; if not, see <http://www.gnu.org/licenses/>.

import decimal
from dateutil.relativedelta import relativedelta
ONE_DAY = relativedelta(days=1)

from django.db import models
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext as _

from lino import dd

from lino.utils import i2d
from lino.utils.instantiator import Instantiator
from lino.core.dbutils import resolve_model
from north.dbutils import babel_values

#~ from lino.modlib.debts.models import AccountTypes
accounts = dd.resolve_app('accounts')

AccountTypes = accounts.AccountTypes

def n2dec(v):
    return decimal.Decimal("%.2d" % v)
   
def objects():
    c = accounts.Chart(name="debts.default")
    yield c
    group = Instantiator('accounts.Group',chart=c).build
    g = group(ref="10",account_type=AccountTypes.incomes,**babel_values('name',
          de=u"Monatliche Einkünfte",
          fr=u"Revenus mensuels",
          en=u"Monthly incomes"
          ))
    yield g
    account = Instantiator('accounts.Account',group=g).build
    yield account(ref="1010",required_for_person=True,**babel_values('name',
          de=u"Gehälter",
          fr=u"Salaires",
          en=u"Salaries"
          ))
    yield account(ref="1020",required_for_person=True,**babel_values('name',
          de=u"Renten",
          fr=u"Pension",
          en=u"Pension"
          ))
    yield account(ref="1030",required_for_person=True,**babel_values('name',
          de=u"Integrationszulage",
          fr=u"Allocation d'intégration",
          en=u"Integration aid"
          ))
    yield account(ref="1040",required_for_person=True,**babel_values('name',
          de=u"Ersatzeinkünfte",
          fr=u"Ersatzeinkünfte",
          en=u"Ersatzeinkünfte"
          ))
    yield account(ref="1050",required_for_person=True,**babel_values('name',
          de=u"Alimente",
          fr=u"Aliments",
          en=u"Aliments"
          ))
    yield account(ref="1060",required_for_person=True,**babel_values('name',
          de=u"Essen-Schecks",
          fr=u"Chèques-repas",
          en=u"Chèques-repas"
          ))
    yield account(ref="1090",required_for_person=True,**babel_values('name',
          de=u"Andere",
          fr=u"Andere",
          en=u"Andere"
          ))

    g = group(ref="20",account_type=AccountTypes.incomes,**babel_values('name',
          de=u"Jährliche Einkünfte",
          fr=u"Revenus annuels",
          en=u"Yearly incomes"
          ))
    yield g
    account = Instantiator('accounts.Account',group=g,periods=12).build
    yield account(ref="2010",required_for_person=True,**babel_values('name',
          de=u"Urlaubsgeld",
          fr=u"Congé payé",
          en=u"Paid holiday"
          ))
    yield account(ref="2020",required_for_person=True,**babel_values('name',
          de=u"Jahresendzulage",
          fr=u"Prime de fin d'année",
          en=u"Year-end prime"
          ))
    yield account(ref="2030",required_for_person=True,**babel_values('name',
          de=u"Gewerkschaftsprämie",
          fr=u"Gewerkschaftsprämie",
          en=u"Gewerkschaftsprämie"
          ))

    g = group(ref="30",account_type=AccountTypes.expenses,**babel_values('name',
          de=u"Monatliche Ausgaben",
          fr=u"Dépenses mensuelles",
          en=u"Monthly expenses"
          ))
    yield g
    account = Instantiator('accounts.Account',group=g).build
    yield account(ref="3010",required_for_household=True,**babel_values('name',
          de=u"Miete",
          fr=u"Loyer",
          en=u"Rent"
          ))
    yield account(ref="3011",required_for_household=True,**babel_values('name',
          de=u"Wasser",
          fr=u"Eau",
          en=u"Water"
          ))
    yield account(ref="3012",required_for_household=True,**babel_values('name',
          de=u"Strom",
          fr=u"Electricité",
          en=u"Electricity"
          ))
    yield account(ref="3020",required_for_household=True,**babel_values('name',
          de=u"Festnetz-Telefon und Internet",
          fr=u"Téléphone fixe et Internet",
          en=u"Telephone & Internet"
          ))
    yield account(ref="3021",required_for_household=True,**babel_values('name',
          de=u"Handy",
          fr=u"GSM",
          en=u"Cell phone"
          ))
    yield account(ref="3030",required_for_household=True,**babel_values('name',
          de=u"Fahrtkosten",
          fr=u"Frais de transport",
          en=u"Transport costs"
          ))
    yield account(ref="3031",required_for_household=True,**babel_values('name',
          de=u"TEC Busabonnement",
          fr=u"Abonnement bus",
          en=u"Public transport"
          ))
    yield account(ref="3032",required_for_household=True,**babel_values('name',
          de=u"Benzin",
          fr=u"Essence",
          en=u"Fuel"
          ))
    yield account(ref="3033",required_for_household=True,**babel_values('name',
          de=u"Unterhalt Auto",
          fr=u"Maintenance voiture",
          en=u"Car maintenance"
          ))
    yield account(ref="3040",required_for_household=True,**babel_values('name',
          de=u"Schulkosten",
          fr=u"École",
          en=u"School"
          ))
    yield account(ref="3041",required_for_household=True,**babel_values('name',
          de=u"Tagesmutter & Kleinkindbetreuung",
          fr=u"Garde enfant",
          en=u"Babysitting"
          ))
    yield account(ref="3050",required_for_household=True,**babel_values('name',
          de=u"Gesundheit",
          fr=u"Santé",
          en=u"Health"
          ))
    yield account(ref="3051",required_for_household=True,**babel_values('name',
          de=u"Kleidung",
          fr=u"Vêtements",
          en=u"Clothes"
          ))
    yield account(ref="3052",required_for_household=True,**babel_values('name',
          de=u"Ernährung",
          fr=u"Alimentation",
          en=u"Food"
          ))
    yield account(ref="3053",required_for_household=True,**babel_values('name',
          de=u"Hygiene",
          fr=u"Hygiène",
          en=u"Hygiene"
          ))
    yield account(ref="3060",required_for_household=True,**babel_values('name',
          de=u"Krankenkassenbeiträge",
          fr=u"Mutuelle",
          en=u"Health insurance"
          ))
    yield account(ref="3061",required_for_household=True,**babel_values('name',
          de=u"Gewerkschaftsbeiträge",
          fr=u"Cotisations syndicat",
          en=u"Labour fees"
          ))
    yield account(ref="3062",required_for_household=True,**babel_values('name',
          de=u"Unterhaltszahlungen",
          fr=u"Unterhaltszahlungen",
          en=u"Unterhaltszahlungen"
          ))
    yield account(ref="3070",required_for_household=True,**babel_values('name',
          de=u"Tabak",
          fr=u"Tabac",
          en=u"Tobacco"
          ))
    yield account(ref="3071",required_for_household=True,**babel_values('name',
          de=u"Freizeit & Unterhaltung",
          fr=u"Loisirs",
          en=u"Spare time"
          ))
    yield account(ref="3072",required_for_household=True,**babel_values('name',
          de=u"Haustiere",
          fr=u"Animaux domestiques",
          en=u"Pets"
          ))
    yield account(ref="3063",required_for_household=True,**babel_values('name',
          de=u"Pensionssparen",
          fr=u"Épargne pension",
          en=u"Retirement savings"
          ))
    yield account(ref="3090",required_for_household=True,**babel_values('name',
          de=u"Sonstige",
          fr=u"Autres",
          en=u"Other"
          ))


    g = group(ref="40",account_type=AccountTypes.expenses,**babel_values('name',
          de=u"Steuern",
          fr=u"Taxes",
          en=u"Taxes"
          ))
    yield g
    account = Instantiator('accounts.Account',group=g,periods=12).build
    yield account(ref="4010",required_for_household=True,**babel_values('name',
          de=u"Gemeindesteuer",
          fr=u"Taxe communale",
          en=u"Municipal tax"
          ))
    yield account(ref="4020",required_for_household=True,**babel_values('name',
          de=u"Kanalisationssteuer",
          fr=u"Kanalisationssteuer",
          en=u"Kanalisationssteuer"
          ))
    yield account(ref="4030",required_for_household=True,**babel_values('name',
          de=u"Müllsteuer",
          fr=u"Taxe déchets",
          en=u"Waste tax"
          ))
    yield account(ref="4040",required_for_household=True,**babel_values('name',
          de=u"Autosteuer",
          fr=u"Taxe circulation",
          en=u"Autosteuer"
          ))
    yield account(ref="4050",required_for_household=True,**babel_values('name',
          de=u"Immobiliensteuer",
          fr=u"Taxe immobilière",
          en=u"Immobiliensteuer"
          ))
    yield account(ref="4090",required_for_household=True,**babel_values('name',
          de=u"Andere",
          fr=u"Autres",
          en=u"Other"
          ))

    g = group(ref="50",account_type=AccountTypes.expenses,**babel_values('name',
          de=u"Versicherungen",
          fr=u"Assurances",
          en=u"Insurances"
          ))
    yield g
    account = Instantiator('accounts.Account',group=g,periods=12).build
    yield account(ref="5010",required_for_household=True,**babel_values('name',
          de=u"Feuer",
          fr=u"Incendie",
          en=u"Fire"
          ))
    yield account(ref="5020",required_for_household=True,**babel_values('name',
          de=u"Familienhaftpflicht",
          fr=u"Responsabilité famille",
          en=u"Familienhaftpflicht"
          ))
    yield account(ref="5030",required_for_household=True,**babel_values('name',
          de=u"Auto",
          fr=u"Voiture",
          en=u"Car insurance"
          ))
    yield account(ref="5040",required_for_household=True,**babel_values('name',
          de=u"Lebensversicherung",
          fr=u"Assurance vie",
          en=u"Life insurance"
          ))
    yield account(ref="5090",required_for_household=True,**babel_values('name',
          de=u"Andere Versicherungen",
          fr=u"Autres assurances",
          en=u"Other insurances"
          ))
          
          
    g = group(ref="60",account_type=AccountTypes.assets,**babel_values('name',
          de=u"Aktiva, Vermögen, Kapital",
          fr=u"Actifs",
          en=u"Assets"
          ))
    yield g
    account = Instantiator('accounts.Account',group=g).build
    yield account(ref="6010",**babel_values('name',
          de=u"Haus",
          fr=u"Maison",
          en=u"House"
          ))
    yield account(ref="6020",**babel_values('name',
          de=u"Auto",
          fr=u"Voiture",
          en=u"Car"
          ))
    
    
    g = group(ref="70",account_type=AccountTypes.liabilities,**babel_values('name',
          de=u"Guthaben, Schulden, Verbindlichkeit",
          fr=u"Créances et dettes",
          en=u"Liabilities"
          ))
    yield g
    account = Instantiator('accounts.Account',group=g).build
    yield account(ref="7010",**babel_values('name',
          de=u"Kredite",
          fr=u"Crédits",
          en=u"Loans"
          ))
    yield account(ref="7020",**babel_values('name',
          de=u"Schulden",
          fr=u"Emprunts",
          en=u"Debts"
          ))
    yield account(ref="7030",**babel_values('name',
          de=u"Gerichtsvollzieher",
          fr=u"Huissier de justice",
          en=u"Bailiff"
          ))
    yield account(ref="7040",**babel_values('name',
          de=u"Zahlungsrückstände",
          fr=u"Factures à payer",
          en=u"Invoices to pay"
          ))

