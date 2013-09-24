# -*- coding: UTF-8 -*-
# all objects() from table jobs_job:
loader.save(create_jobs_job(1,1,1,u'Kellner',1,185,1,None,1,u'Sehr harte Stelle'))
loader.save(create_jobs_job(5,5,1,u'Kellner',5,186,5,None,1,u''))
loader.save(create_jobs_job(2,2,2,u'Koch',2,186,2,None,1,u''))
loader.save(create_jobs_job(6,6,2,u'Koch',1,188,1,None,1,u''))
loader.save(create_jobs_job(3,3,3,u'K\xfcchenassistent',3,188,3,None,1,u'No supervisor. Only for independent people.'))
loader.save(create_jobs_job(7,7,3,u'K\xfcchenassistent',2,185,2,None,1,u'Sehr harte Stelle'))
loader.save(create_jobs_job(4,4,4,u'Tellerw\xe4scher',4,185,4,None,1,u''))
loader.save(create_jobs_job(8,8,4,u'Tellerw\xe4scher',3,186,3,None,1,u''))

loader.flush_deferred_objects()
