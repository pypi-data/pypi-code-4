# -*- coding: UTF-8 -*-
# all objects() from table properties_propchoice:
loader.save(create_properties_propchoice(1,3,u'1',[u'Furniture', u'Meubles', u'M\xf6bel', u'']))
loader.save(create_properties_propchoice(2,3,u'2',[u'Web hosting', u'Hosting', u'Hosting', u'']))

loader.flush_deferred_objects()
