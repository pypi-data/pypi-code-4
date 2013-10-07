# -*- coding: UTF-8 -*-
# all objects() from table households_role:
loader.save(create_households_role(1,[u'Head of household', u'Chef de m\xe9nage', u'Haushaltsvorstand', u''],True))
loader.save(create_households_role(2,[u'Spouse', u'Conjoint', u'Ehepartner', u''],True))
loader.save(create_households_role(3,[u'Partner', u'Partenaire', u'Partner', u''],True))
loader.save(create_households_role(4,[u'Cohabitant', u'Cohabitant', u'Mitbewohner', u''],False))
loader.save(create_households_role(5,[u'Child', u'Enfant', u'Kind', u''],False))
loader.save(create_households_role(6,[u'Adopted child', u'Enfant adopt\xe9', u'Adoptivkind', u''],False))

loader.flush_deferred_objects()
