# -*- coding: UTF-8 -*-
# all objects() from table users_team:
loader.save(create_users_team(1,[u'GSS (General Social Service)', u'SSG (Service social g\xe9n\xe9ral)', u'ASD (Allgemeiner Sozialdienst)', u'ASD (Algemene Sociale Dienst)']))
loader.save(create_users_team(2,[u'Integration service', u'Service int\xe9gration', u'DSBE (Dienst f\xfcr Sozial-Berufliche Eingliederung)', u'']))
loader.save(create_users_team(3,[u'Debts mediation', u'M\xe9diation de dettes', u'Schuldnerberatung', u'']))

loader.flush_deferred_objects()
