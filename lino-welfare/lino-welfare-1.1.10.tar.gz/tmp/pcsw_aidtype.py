# -*- coding: UTF-8 -*-
# all objects() from table pcsw_aidtype:
loader.save(create_pcsw_aidtype(1,[u"Revenu d'int\xe9gration cat. 1 (couple)", u"Revenu d'int\xe9gration cat. 1 (couple)", u'Eingliederungseinkommen Kat 1 (Zusammenlebend)', u'']))
loader.save(create_pcsw_aidtype(2,[u"Revenu d'int\xe9gration cat. 2 (c\xe9libataire)", u"Revenu d'int\xe9gration cat. 2 (c\xe9libataire)", u'Eingliederungseinkommen Kat 2 (Alleinlebend)', u'']))
loader.save(create_pcsw_aidtype(3,[u"Revenu d'int\xe9gration cat. 3 (famille \xe0 charge)", u"Revenu d'int\xe9gration cat. 3 (famille \xe0 charge)", u'Eingliederungseinkommen Kat 3 (Familie zu Lasten)', u'']))
loader.save(create_pcsw_aidtype(4,[u'Aide aux immigrants cat. 1 (couple)', u'Aide aux immigrants cat. 1 (couple)', u'Ausl\xe4nderbeihilfe Kat 1 (Zusammenlebend)', u'']))
loader.save(create_pcsw_aidtype(5,[u'Aide aux immigrants cat. 2 (c\xe9libataire)', u'Aide aux immigrants cat. 2 (c\xe9libataire)', u'Ausl\xe4nderbeihilfe Kat 2 (Alleinlebend)', u'']))
loader.save(create_pcsw_aidtype(6,[u'Aide aux immigrants cat. 3 (famille \xe0 charge)', u'Aide aux immigrants cat. 3 (famille \xe0 charge)', u'Ausl\xe4nderbeihilfe Kat 3 (Familie zu Lasten)', u'']))
loader.save(create_pcsw_aidtype(7,[u'Autre aide sociale', u'Autre aide sociale', u'Sonstige Sozialhilfe', u'']))

loader.flush_deferred_objects()
