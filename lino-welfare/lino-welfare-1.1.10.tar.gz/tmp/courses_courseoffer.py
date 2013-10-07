# -*- coding: UTF-8 -*-
# all objects() from table courses_courseoffer:
loader.save(create_courses_courseoffer(1,u'Deutsch f\xfcr Anf\xe4nger',1,214,u''))
loader.save(create_courses_courseoffer(2,u'Deutsch f\xfcr Anf\xe4nger',1,215,u''))
loader.save(create_courses_courseoffer(3,u'Fran\xe7ais pour d\xe9butants',2,215,u''))

loader.flush_deferred_objects()
