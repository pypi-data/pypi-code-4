# -*- coding: UTF-8 -*-
# all objects() from table cal_guest:
loader.save(create_cal_guest(1,None,59,116,1,'10',u'',None,None,None))
loader.save(create_cal_guest(2,None,94,127,1,'10',u'',None,None,None))
loader.save(create_cal_guest(3,None,101,150,1,'10',u'',None,None,None))
loader.save(create_cal_guest(4,None,136,136,1,'10',u'',None,None,None))
loader.save(create_cal_guest(5,None,143,137,1,'10',u'',None,None,None))
loader.save(create_cal_guest(6,None,154,115,1,'60',u'',dt(2013,8,20,14,9,42),dt(2013,8,20,14,15,40),None))
loader.save(create_cal_guest(7,None,156,178,1,'20',u'',None,None,None))

loader.flush_deferred_objects()
