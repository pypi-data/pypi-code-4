# -*- coding: UTF-8 -*-
# all objects() from table uploads_uploadtype:
loader.save(create_uploads_uploadtype(1,u'Personalausweis'))
loader.save(create_uploads_uploadtype(2,u'Aufenthaltserlaubnis'))
loader.save(create_uploads_uploadtype(3,u'Arbeitserlaubnis'))
loader.save(create_uploads_uploadtype(4,u'Vertrag'))
loader.save(create_uploads_uploadtype(5,u'F\xfchrerschein'))

loader.flush_deferred_objects()
