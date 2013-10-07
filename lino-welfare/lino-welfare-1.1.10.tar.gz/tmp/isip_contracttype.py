# -*- coding: UTF-8 -*-
# all objects() from table isip_contracttype:
loader.save(create_isip_contracttype(1,[u'VSE Ausbildung', u'VSE Ausbildung', u'VSE Ausbildung', u''],u'appypdf',u'vse.odt',u'vsea',1,True))
loader.save(create_isip_contracttype(2,[u'VSE Arbeitssuche', u'VSE Arbeitssuche', u'VSE Arbeitssuche', u''],u'appypdf',u'vse.odt',u'vseb',1,False))
loader.save(create_isip_contracttype(3,[u'VSE Lehre', u'VSE Lehre', u'VSE Lehre', u''],u'appypdf',u'vse.odt',u'vsec',1,False))
loader.save(create_isip_contracttype(4,[u'VSE Vollzeitstudium', u'VSE Vollzeitstudium', u'VSE Vollzeitstudium', u''],u'appypdf',u'vse.odt',u'vsed',1,True))
loader.save(create_isip_contracttype(5,[u'VSE Sprachkurs', u'VSE Sprachkurs', u'VSE Sprachkurs', u''],u'appypdf',u'vse.odt',u'vsee',1,False))

loader.flush_deferred_objects()
