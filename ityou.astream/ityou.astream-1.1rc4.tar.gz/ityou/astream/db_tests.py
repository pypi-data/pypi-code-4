# -*- coding: utf-8 -*-
from datetime import datetime, timedelta 
import logging

from .dbapi import DBApi

class DBTest():
    """Tests for the DB
    """
    
    def __init__(self):    
        self.db = DBApi()
        self.tdelta = datetime.now() - timedelta(seconds = 3600)

        self.test_getActivities()
        self.test_countActivities()
        self.test_addActivity()
        
        self.test_getActivityComments()
        self.test_addComment() 
        self.test_updateComment()
         
    def test_getActivities(self):
        logging.info("\n\n ACTIVITIES: \n\t\t %s \n" % str(        [ str(a) for a in self.db.getActivities(timestamp=self.tdelta) ]          ))
        
    def test_countActivities(self):
        logging.info("\n\n NUMBER OF ACTIVITIES: \n\t\t %s \n" % self.db.countActivities())
    
    def test_addActivity(self):
        act = {
               'user_id':       u'lmuller2000',
               'user_name':     u'Leo Pol',
               'user_email':    u'lm@ityou.de',
               'content_uid':   u'3434-73-6323',
               'content_title': u'Das Gaga',
               'content_path':  u'/der/gaga/',
               'message':       u'tHIS IS TE Mässäch',
               }
        
        logging.info("\n\n ADD ACTIVITY \n\t\t: %s \n" %    str(self.db.addActivity(act)))
        
    def test_addComment(self):
        com = {
               'activity_md5':  u'c7b49536316dd0a0e51c894fec6a1899',
               'user_id':       u'lmuller22',
               'user_name':     u'Luc Möller',
               'user_email':    u'info@ityou.de',
               'comment':       u'Ganz schön Tricky GAGA',
               }
        logging.info("\n\n ADD KOMMENTAR \n\t\t: %s \n" %    str(self.db.addComment(com)))
        
    def test_updateComment(self):
        logging.info("\n\n UPDATE KOMMENTAR \n\t\t: %s \n" %    self.db.updateComment(u'7cae723aee079563cb44939212edefff', u'Das ist ein neuer Kommentar<br />'))

    def test_getActivityComments(self):
        logging.info(str("\n\n KOMMENTARE \n\t\t: %s\n" %    self.db.getActivityComments('c7b49536316dd0a0e51c894fec6a1899')))
    
    def test_getLatestActivityComment(self):
        logging.info("\n\n LETZTER KOMMENTAR \n\t\t: %s\n" %    str(self.db.getLatestActivityComment('c7b49536316dd0a0e51c894fec6a1899')))    

##-------------
##db_tests = DBTest()
    
