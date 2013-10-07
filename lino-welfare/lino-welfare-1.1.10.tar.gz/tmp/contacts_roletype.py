# -*- coding: UTF-8 -*-
# all objects() from table contacts_roletype:
loader.save(create_contacts_roletype(1,[u'Manager', u'G\xe9rant', u'Gesch\xe4ftsf\xfchrer', u''],True))
loader.save(create_contacts_roletype(2,[u'Director', u'Directeur', u'Direktor', u''],True))
loader.save(create_contacts_roletype(3,[u'Secretary', u'Secr\xe9taire', u'Sekret\xe4r', u''],True))
loader.save(create_contacts_roletype(4,[u'IT Manager', u'G\xe9rant informatique', u'EDV-Manager', u''],False))
loader.save(create_contacts_roletype(5,[u'President', u'Pr\xe9sident', u'Pr\xe4sident', u''],True))

loader.flush_deferred_objects()
