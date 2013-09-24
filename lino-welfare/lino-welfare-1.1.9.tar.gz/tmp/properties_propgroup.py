# -*- coding: UTF-8 -*-
# all objects() from table properties_propgroup:
loader.save(create_properties_propgroup(1,[u'Skills', u'Comp\xe9tences professionnelles', u'Fachkompetenzen', u'']))
loader.save(create_properties_propgroup(2,[u'Soft skills', u'Comp\xe9tences sociales', u'Sozialkompetenzen', u'']))
loader.save(create_properties_propgroup(3,[u'Obstacles', u'Obstacles', u'Hindernisse', u'']))

loader.flush_deferred_objects()
