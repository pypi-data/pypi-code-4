# -*- coding: UTF-8 -*-
# all objects() from table cal_priority:
loader.save(create_cal_priority(1,[u'very urgent', u'tr\xe8s urgent', u'sehr dringend', u''],u'1'))
loader.save(create_cal_priority(2,[u'quite urgent', u'relativement urgent', u'recht dringend', u''],u'2'))
loader.save(create_cal_priority(3,[u'relatively urgent', u'relativement urgent', u'ziemlich dringend', u''],u'3'))
loader.save(create_cal_priority(4,[u'relatively urgent', u'relativement urgent', u'ziemlich dringend', u''],u'4'))
loader.save(create_cal_priority(5,[u'normal', u'normal', u'normal', u''],u'5'))
loader.save(create_cal_priority(6,[u'not very urgent', u'pas tr\xe8s urgent', u'nicht sehr niedrig', u''],u'6'))
loader.save(create_cal_priority(7,[u'not urgent', u'pas urgent', u'nicht dringend', u''],u'7'))
loader.save(create_cal_priority(8,[u'not urgent', u'pas urgent', u'nicht dringend', u''],u'8'))
loader.save(create_cal_priority(9,[u'not urgent at all', u'pas urgent du tout', u'\xfcberhaupt nicht dringend', u''],u'9'))

loader.flush_deferred_objects()
