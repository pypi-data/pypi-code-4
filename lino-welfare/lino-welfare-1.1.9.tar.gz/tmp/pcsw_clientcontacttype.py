# -*- coding: UTF-8 -*-
# all objects() from table pcsw_clientcontacttype:
loader.save(create_pcsw_clientcontacttype(1,[u'Krankenkasse', u'', u'', u'']))
loader.save(create_pcsw_clientcontacttype(2,[u'Apotheke', u'', u'', u'']))
loader.save(create_pcsw_clientcontacttype(3,[u'Rechtsanwalt', u'', u'', u'']))
loader.save(create_pcsw_clientcontacttype(4,[u'Bailiff', u'Huissier de justice', u'Gerichtsvollzieher', u'']))
loader.save(create_pcsw_clientcontacttype(5,[u'Arbeitsvermittler', u'', u'', u'']))

loader.flush_deferred_objects()
