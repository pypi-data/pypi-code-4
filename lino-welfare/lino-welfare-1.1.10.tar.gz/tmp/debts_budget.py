# -*- coding: UTF-8 -*-
# all objects() from table debts_budget:
loader.save(create_debts_budget(1,10,None,date(2013,8,18),181,False,False,False,u'',u'','120'))
loader.save(create_debts_budget(2,10,None,date(2013,8,18),182,False,False,False,u'',u'','120'))
loader.save(create_debts_budget(3,10,dt(2013,8,24,4,16,28),date(2013,8,18),183,False,False,False,u'',u'','120'))

loader.flush_deferred_objects()
