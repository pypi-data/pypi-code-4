# -*- coding: UTF-8 -*-
# all objects() from table pcsw_dispensereason:
loader.save(create_pcsw_dispensereason(1,[u'Health', u'Sant\xe9', u'Gesundheitlich', u''],1))
loader.save(create_pcsw_dispensereason(2,[u'Studies', u'Etude/Formation', u'Studium/Ausbildung', u''],2))
loader.save(create_pcsw_dispensereason(3,[u'Familiar', u'Cause familiale', u'Famili\xe4r', u''],3))
loader.save(create_pcsw_dispensereason(4,[u'Other', u'Autre', u'Sonstige', u''],4))

loader.flush_deferred_objects()
