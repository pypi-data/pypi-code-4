# -*- coding: UTF-8 -*-
# all objects() from table jobs_study:
loader.save(create_jobs_study(1,None,None,176,1,u'Abitur',date(1974,9,1),date(1986,6,30),False,None,u'',None))
loader.save(create_jobs_study(2,None,None,115,1,u'Abitur',date(1974,9,1),date(1986,6,30),False,None,u'',None))

loader.flush_deferred_objects()
