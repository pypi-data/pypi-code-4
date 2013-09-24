# -*- coding: UTF-8 -*-
# all objects() from table jobs_schedule:
loader.save(create_jobs_schedule(1,[u'5 days/week', u'5 jours/semaine', u'5-Tage-Woche', u'']))
loader.save(create_jobs_schedule(2,[u'Individual', u'individuel', u'Individuell', u'']))
loader.save(create_jobs_schedule(3,[u'Monday, Wednesday, Friday', u'lundi,mercredi,vendredi', u'Montag, Mittwoch, Freitag', u'']))

loader.flush_deferred_objects()
