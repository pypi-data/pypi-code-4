# -*- coding: UTF-8 -*-
# all objects() from table system_textfieldtemplate:
loader.save(create_system_textfieldtemplate(1,None,u'hello',u"Inserts 'Hello, world!'",None,u'<div>Hello, world!</div>'))
loader.save(create_system_textfieldtemplate(2,None,u'mfg',None,None,u'<p>Mit freundlichen Gr&uuml;&szlig;en<br><p>{{request.subst_user or request.user}}</p>'))

loader.flush_deferred_objects()
