# -*- coding: UTF-8 -*-
# all objects() from table pcsw_persongroup:
loader.save(create_pcsw_persongroup(1,u'Auswertung',u'1',True))
loader.save(create_pcsw_persongroup(2,u'Ausbildung',u'2',True))
loader.save(create_pcsw_persongroup(3,u'Suche',u'4',True))
loader.save(create_pcsw_persongroup(4,u'Arbeit',u'4bis',True))
loader.save(create_pcsw_persongroup(5,u'Standby',u'9',True))

loader.flush_deferred_objects()
