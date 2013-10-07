# -*- coding: UTF-8 -*-
# all objects() from table pcsw_coachingending:
loader.save(create_pcsw_coachingending(1,[u'Transfer to colleague', u'Transfert vers coll\xe8gue', u'\xdcbergabe an Kollege', u''],1,None))
loader.save(create_pcsw_coachingending(2,[u'End of right on social aid', u"Arret du droit \xe0 l'aide sociale", u'Einstellung des Anrechts auf SH', u''],2,None))
loader.save(create_pcsw_coachingending(3,[u'Moved to another town', u'D\xe9m\xe9nagement vers autre commune', u'Umzug in andere Gemeinde', u''],3,None))
loader.save(create_pcsw_coachingending(4,[u'Found a job', u'A trouv\xe9 du travail', u'Hat selber Arbeit gefunden', u''],4,None))

loader.flush_deferred_objects()
