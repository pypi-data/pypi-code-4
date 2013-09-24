# -*- coding: UTF-8 -*-
# all objects() from table newcomers_faculty:
loader.save(create_newcomers_faculty(1,[u'EiEi', u"Revenu d'int\xe9gration sociale (RIS)", u'Eingliederungseinkommen (EiEi)', u''],10))
loader.save(create_newcomers_faculty(2,[u'DSBE', u"Service d'insertion socio-professionnelle", u'DSBE', u''],5))
loader.save(create_newcomers_faculty(3,[u'Ausl\xe4nderbeihilfe', u'Aide sociale \xe9quivalente (pour \xe9trangers)', u'Ausl\xe4nderbeihilfe', u''],4))
loader.save(create_newcomers_faculty(4,[u'Finanzielle Begleitung', u'Accompagnement budg\xe9taire', u'Finanzielle Begleitung', u''],6))
loader.save(create_newcomers_faculty(5,[u'Laufende Beihilfe', u'Aide compl\xe9menataire', u'Laufende Beihilfe', u''],2))

loader.flush_deferred_objects()
