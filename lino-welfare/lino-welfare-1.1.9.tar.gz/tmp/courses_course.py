# -*- coding: UTF-8 -*-
# all objects() from table courses_course:
loader.save(create_courses_course(1,1,u'',date(2013,9,17),u''))
loader.save(create_courses_course(2,2,u'',date(2013,9,3),u''))
loader.save(create_courses_course(3,3,u'',date(2013,9,3),u''))

loader.flush_deferred_objects()
