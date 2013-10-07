# -*- coding: UTF-8 -*-
# all objects() from table jobs_function:
loader.save(create_jobs_function(1,[u'Waiter', u'Serveur', u'Kellner', u''],u'',5))
loader.save(create_jobs_function(2,[u'Cook', u'Cuisinier', u'Koch', u''],u'',5))
loader.save(create_jobs_function(3,[u'Cook assistant', u'Aide Cuisinier', u'K\xfcchenassistent', u''],u'',5))
loader.save(create_jobs_function(4,[u'Dishwasher', u'Plongeur', u'Tellerw\xe4scher', u''],u'',5))

loader.flush_deferred_objects()
