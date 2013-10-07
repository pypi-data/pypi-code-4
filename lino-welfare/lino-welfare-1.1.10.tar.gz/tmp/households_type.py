# -*- coding: UTF-8 -*-
# all objects() from table households_type:
loader.save(create_households_type(1,[u'Married couple', u'Couple mari\xe9', u'Ehepaar', u'']))
loader.save(create_households_type(2,[u'Family', u'Famille', u'Familie', u'']))
loader.save(create_households_type(3,[u'Factual household', u'M\xe9nage de fait', u'Faktischer Haushalt', u'']))
loader.save(create_households_type(4,[u'Legal cohabitation', u'Cohabitation l\xe9gale', u'Legale Wohngemeinschaft', u'']))

loader.flush_deferred_objects()
