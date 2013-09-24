# -*- coding: UTF-8 -*-
# all objects() from table isip_exampolicy:
loader.save(create_isip_exampolicy(1,[u'every month', u'mensuel', u'monatlich', u''],date(2013,8,18),time(9,0,0),None,None,u'M',1,False,False,False,False,False,False,False,None,1))
loader.save(create_isip_exampolicy(2,[u'every 2 months', u'bimensuel', u'zweimonatlich', u''],date(2013,8,18),time(9,0,0),None,None,u'M',2,False,False,False,False,False,False,False,None,1))
loader.save(create_isip_exampolicy(3,[u'every 3 months', u'tous les 3 mois', u'alle 3 Monate', u''],date(2013,8,18),time(9,0,0),None,None,u'M',3,False,False,False,False,False,False,False,None,1))
loader.save(create_isip_exampolicy(4,[u'every 2 weeks', u'hebdomadaire', u'zweiw\xf6chentlich', u''],date(2013,8,18),time(9,0,0),None,None,u'W',2,False,False,False,False,False,False,False,None,1))
loader.save(create_isip_exampolicy(5,[u'other', u'autre', u'andere', u''],date(2013,8,18),None,None,None,u'M',0,False,False,False,False,False,False,False,None,None))

loader.flush_deferred_objects()
