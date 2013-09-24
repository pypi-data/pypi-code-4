# -*- coding: UTF-8 -*-
# all objects() from table cal_calendar:
loader.save(create_cal_calendar(1,[u'Internal meetings with client', u'Rencontres internes avec client', u'Klientengespr\xe4che intern', u''],1,u'',u'',False,u'',u'local',u'',u'',u'',u'',False,None,20,[u'Termin', u'', u'', u''],None,True))
loader.save(create_cal_calendar(2,[u'External meetings with client', u'Rencontres client externes', u'Klientengespr\xe4che extern', u''],2,u'',u'',False,u'',u'local',u'',u'',u'',u'',False,None,1,[u'Termin', u'', u'', u''],None,True))
loader.save(create_cal_calendar(3,[u'Internal meetings', u'R\xe9unions internes', u'Versammlung intern', u''],3,u'',u'',False,u'',u'local',u'',u'',u'',u'',False,None,4,[u'Termin', u'', u'', u''],None,False))
loader.save(create_cal_calendar(4,[u'External meetings', u'R\xe9unions externes', u'Versammlung extern', u''],4,u'',u'',False,u'',u'local',u'',u'',u'',u'',False,None,8,[u'Termin', u'', u'', u''],None,False))
loader.save(create_cal_calendar(5,[u'Team Meetings', u'Coordinations en \xe9quipe', u'Team-Besprechungen', u''],5,u'',u'',False,u'Team.eml.html',u'local',u'',u'',u'',u'',False,None,12,[u'Termin', u'', u'', u''],None,False))
loader.save(create_cal_calendar(6,[u'Private', u'Priv\xe9', u'Privat', u''],6,u'',u'',False,u'',u'local',u'',u'',u'',u'',False,None,25,[u'Termin', u'', u'', u''],None,False))

loader.flush_deferred_objects()
