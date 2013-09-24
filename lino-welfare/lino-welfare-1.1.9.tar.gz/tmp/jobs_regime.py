# -*- coding: UTF-8 -*-
# all objects() from table jobs_regime:
loader.save(create_jobs_regime(1,[u'20 hours/week', u'20 heures/semaine', u'20 Stunden/Woche', u'']))
loader.save(create_jobs_regime(2,[u'35 hours/week', u'35 heures/semaine', u'35 Stunden/Woche', u'']))
loader.save(create_jobs_regime(3,[u'38 hours/week', u'38 heures/semaine', u'38 Stunden/Woche', u'']))

loader.flush_deferred_objects()
