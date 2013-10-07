# -*- coding: UTF-8 -*-
# all objects() from table debts_actor:
loader.save(create_debts_actor(1,1,1,112,u'Herr',u''))
loader.save(create_debts_actor(2,2,1,113,u'Frau',u''))
loader.save(create_debts_actor(3,1,2,114,u'Herr',u''))
loader.save(create_debts_actor(4,2,2,117,u'Frau',u''))
loader.save(create_debts_actor(5,1,3,115,u'Herr',u''))
loader.save(create_debts_actor(6,2,3,118,u'Frau',u''))

loader.flush_deferred_objects()
