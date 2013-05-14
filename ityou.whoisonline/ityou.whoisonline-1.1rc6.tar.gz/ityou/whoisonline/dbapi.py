# -*- coding: utf-8 -*-
import logging
import hashlib
import os

from config import DEBUG, USER_ID_BLACKLIST
from config import DB_LOCATION, DB, TABLE
from datetime import datetime, timedelta

# --- sqlalchemy -----
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Unicode, UnicodeText, Boolean
from sqlalchemy import ForeignKey
from sqlalchemy import desc, and_,  or_
from sqlalchemy import func
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm import sessionmaker

Base = declarative_base()
# ---- /sqlalchemy --------

try:
    os.mkdir(DB_LOCATION)
except OSError:
    logging.info("%s already exists. No nedd to create." % DB_LOCATION)


class OnlineUser(Base):
    """ An online user Object
    """
    __tablename__ = 'whoisonline'
    
    id              = Column(Integer, primary_key=True)
    user_id         = Column(Unicode)
    email           = Column(Unicode)
    doc_path        = Column(Unicode)
    timestamp       = Column(DateTime)
    

class DBApi(object):
    """ DB Util
    """
    
    def __init__(self):
        """Initialize Database
        """
        engine  = create_engine(DB, echo=DEBUG, encoding="utf-8")
        self.Session = sessionmaker(bind=engine)
        
        # create dbs if not exist ----
        Base.metadata.create_all(engine)
        
        # prepare utils
        self.db_utils = DBUtils()


    def getOnlineUsers(self,timeout):
        """ get the users who are online
        timeout:int : 3600 = 1 Std.
        """
        timeout = datetime.now() - timedelta(seconds=timeout)
        
        try:
            se = self.Session()
            online_users = se.query(OnlineUser.user_id, OnlineUser.timestamp )\
                                .group_by(OnlineUser.user_id)\
                                .filter(OnlineUser.timestamp > timeout)\
                                .order_by(desc(OnlineUser.timestamp))
        except:
            logging.error("Retrieving Online users not possible")
        finally:
            se.close()

        # returns data over webservice (dict is serializable)    
        return [ {"user_id" :  ou[0], "timestamp" : ou[1]} for ou in online_users]



    def getUserProfile(self,timeout,user_id):
        """ get the users profile
        """
        timeout = datetime.now() - timedelta(seconds=timeout)
       
        try:
            se = self.Session()
            user_profile = se.query(OnlineUser)\
                            .group_by(OnlineUser.user_id)\
                            .filter(OnlineUser.user_id == user_id)\
                            .filter(OnlineUser.timestamp > timeout)\
                            .order_by(desc(OnlineUser.timestamp)).one()
        except:
            logging.error("Retrieving User profile not possible")
            user_profile = None        
        finally:
            se.close()

        # returns data over webservice (dict is serializable)    
        return  self.db_utils.convertAttributesToDict(user_profile)  

    
    def addOnlineUser(self,ou):
        """ Add an Online_user wit a doc_path
        into the database
        ou must be a dict
        """
               
        timestamp = datetime.now()
         
        online_user = OnlineUser(
                user_id     = ou['user_id'],
                email       = ou['email'],
                doc_path    = ou['doc_path'],
                timestamp   = timestamp,
                )
        try:
            se = self.Session()
            se.add(online_user)
            id = online_user.id

            se.commit()
        except:
            logging.error("Could not insert online user  %s" % str(online_user))
        finally:
            se.close()
        
        return { 'id':id, 'timestamp': timestamp }

class DBUtils():
    """ Help functions
    """        
    def convertAttributesToDict(self, object):
        """Returns all public attributes of an object as a dict of attributes"""
        try:
            adict = dict((key, value) for key, value in object.__dict__.iteritems() 
                       if not callable(value) and not key.startswith('_'))
            return adict        
        except:
            return None
        



