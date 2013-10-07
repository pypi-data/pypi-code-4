# -*- coding: UTF-8 -*-
# all objects() from table pcsw_exclusiontype:
loader.save(create_pcsw_exclusiontype(1,u'Termin nicht eingehalten'))
loader.save(create_pcsw_exclusiontype(2,u'ONEM-Auflagen nicht erf\xfcllt'))

loader.flush_deferred_objects()
