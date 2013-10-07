# -*- coding: UTF-8 -*-
# all objects() from table courses_coursecontent:
loader.save(create_courses_coursecontent(1,u'Deutsch'))
loader.save(create_courses_coursecontent(2,u'Franz\xf6sisch'))

loader.flush_deferred_objects()
