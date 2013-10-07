# -*- coding: UTF-8 -*-
# all objects() from table isip_contractending:
loader.save(create_isip_contractending(1,u'Normaler MWSt-Satz',True,True,False,False))
loader.save(create_isip_contractending(2,u'Alkohol',True,True,False,True))
loader.save(create_isip_contractending(3,u'Gesundheit',True,True,False,True))
loader.save(create_isip_contractending(4,u'H\xf6here Gewalt',True,True,False,True))

loader.flush_deferred_objects()
