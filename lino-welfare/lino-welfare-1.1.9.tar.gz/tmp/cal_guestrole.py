# -*- coding: UTF-8 -*-
# all objects() from table cal_guestrole:
loader.save(create_cal_guestrole(1,[u'Visitor', u'Visiteur', u'Besucher', u''],u'',u'',False,u'Visitor.eml.html'))
loader.save(create_cal_guestrole(2,[u'Colleague', u'Coll\xe8gue', u'Kollege', u''],u'',u'',False,u''))
loader.save(create_cal_guestrole(3,[u'Presider', u'Pr\xe9sident', u'Vorsitzender', u''],u'',u'',False,u''))
loader.save(create_cal_guestrole(4,[u'Reporter', u'Greffier', u'Protokollf\xfchrer', u''],u'',u'',False,u''))

loader.flush_deferred_objects()
