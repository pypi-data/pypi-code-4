# -*- coding: UTF-8 -*-
# all objects() from table jobs_jobtype:
loader.save(create_jobs_jobtype(1,1,u'Sozialwirtschaft = "major\xe9s"',u''))
loader.save(create_jobs_jobtype(2,2,u'Intern',u''))
loader.save(create_jobs_jobtype(3,3,u'Extern (\xd6ffentl. VoE mit Kostenr\xfcckerstattung)',u''))
loader.save(create_jobs_jobtype(4,4,u'Extern (Privat Kostenr\xfcckerstattung)',u''))
loader.save(create_jobs_jobtype(5,5,u'Sonstige',u''))

loader.flush_deferred_objects()
