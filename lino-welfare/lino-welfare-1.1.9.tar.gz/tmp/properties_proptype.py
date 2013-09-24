# -*- coding: UTF-8 -*-
# all objects() from table properties_proptype:
loader.save(create_properties_proptype(1,[u'Present or not', u'Pr\xe9sent ou pas', u'Vorhanden oder nicht', u'Ja of niet'],u'',u'',False,False))
loader.save(create_properties_proptype(2,[u'Rating', u'Appr\xe9ciation(?)', u'Bewertung', u'Hoe goed'],u'properties.HowWell',u'2',False,False))
loader.save(create_properties_proptype(3,[u'Division', u'Division', u'Abteilung', u''],u'',u'',False,False))

loader.flush_deferred_objects()
