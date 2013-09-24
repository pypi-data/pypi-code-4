# -*- coding: UTF-8 -*-
# all objects() from table accounts_group:
loader.save(create_accounts_group(1,[u'Monthly incomes', u'Revenus mensuels', u'Monatliche Eink\xfcnfte', u''],1,u'10',u'I',u''))
loader.save(create_accounts_group(2,[u'Yearly incomes', u'Revenus annuels', u'J\xe4hrliche Eink\xfcnfte', u''],1,u'20',u'I',u''))
loader.save(create_accounts_group(3,[u'Monthly expenses', u'D\xe9penses mensuelles', u'Monatliche Ausgaben', u''],1,u'30',u'E',u''))
loader.save(create_accounts_group(4,[u'Taxes', u'Taxes', u'Steuern', u''],1,u'40',u'E',u''))
loader.save(create_accounts_group(5,[u'Insurances', u'Assurances', u'Versicherungen', u''],1,u'50',u'E',u''))
loader.save(create_accounts_group(6,[u'Assets', u'Actifs', u'Aktiva, Verm\xf6gen, Kapital', u''],1,u'60',u'A',u''))
loader.save(create_accounts_group(7,[u'Liabilities', u'Cr\xe9ances et dettes', u'Guthaben, Schulden, Verbindlichkeit', u''],1,u'70',u'L',u''))

loader.flush_deferred_objects()
