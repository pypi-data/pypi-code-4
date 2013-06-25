# -*- coding: utf-8 -*-
import os
import logging
import hashlib
from datetime import datetime, timedelta 
from Acquisition import aq_inner
from config import DEBUG, USER_ID_BLACKLIST

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Unicode, UnicodeText
from sqlalchemy import ForeignKey
from sqlalchemy import desc
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm import sessionmaker

from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from ityou.astream.interfaces import IAstreamSettings

DB_LOCATION         = '/'.join(INSTANCE_HOME.split('/')[:-2]) + "/var/sqlite3"
DB_ASTREAM          = "sqlite:///"+ DB_LOCATION +  "/ityou.astream.db"
TABLE_ACTIVITIES    = 'activities'
TABLE_COMMENTS      = 'comments'

Base = declarative_base()

try:
    os.mkdir(DB_LOCATION)
except OSError:
    logging.info("%s already exists. No nedd to create." % DB_LOCATION)

class Activity(Base):
    """ An activity Object
    """
    __tablename__ = 'activities'
    
    id              = Column(Integer, primary_key=True)
    md5             = Column(Unicode)
    user_id         = Column(Unicode)
    user_name       = Column(Unicode)
    user_email      = Column(Unicode)
    content_uid     = Column(Unicode)
    content_title   = Column(Unicode)
    content_path    = Column(Unicode)
    message         = Column(UnicodeText)
    comments        = relationship("Comment",backref="activities")
    timestamp       = Column(DateTime)

class Comment(Base):
    """ A Comment to the activities
    """
    __tablename__ = 'comments'
    
    id              = Column(Integer, primary_key=True)
    activity_md5    = Column(Unicode, ForeignKey('activities.md5'))
    user_id         = Column(Unicode)
    user_name       = Column(Unicode)
    user_email      = Column(Unicode)
    comment         = Column(UnicodeText)
    timestamp       = Column(DateTime)
    md5             = Column(Unicode)

class DBApi(object):
    """ DB Util
    """
    def __init__(self):
        """Initialize Database
        """
        engine  = create_engine(DB_ASTREAM, echo=False, encoding="utf-8")
        self.Session = sessionmaker(bind=engine)

        Base.metadata.create_all(engine)

    def getActivities(self, \
                      context=None, \
                      timestamp=None, \
                      newer=True,  \
                      order_field="id", \
                      descending=True, \
                      user_id="", \
                      content_group=True, \
                      max=50, offset=0):
        """ return the latest MAX activities
        OLD: getActivityStream + getLatestActivities
        """
        activities = None
        if max > 50: max = 50 # never > 50 !

        if context:
            context_path ='/'.join(context.getPhysicalPath())
                
        se = self.Session()
        q = se.query(Activity)
        
        if user_id:
            q = q.filter(Activity.user_id == user_id)
            
        if timestamp:
            if newer:
                q = q.filter(Activity.timestamp > timestamp)
            else:
                q = q.filter(Activity.timestamp < timestamp)
                
        if context:
            q = q.filter(Activity.content_path.like( context_path + '%'  ))
            
        if order_field and descending:
            q = q.order_by(desc(getattr(Activity,order_field)))
            
        if content_group:
            q = q.group_by(Activity.content_uid, Activity.message)
                    
        activities = q[offset:offset+max]
        
        db_utils = DBUtils()                        
        activity_list = []
        
        for activity in activities:
            comment_list = []
            comments = activity.comments
            for comment in comments:
                comment_list.append(db_utils.convertAttributesToDict(comment))
            act =  db_utils.convertAttributesToDict(activity)
            act['comments'] = comment_list     

            activity_list.append(act)
        
        se.close()

        return activity_list

    def countActivities(self):
        """ return the number of activities
        OLD:checkDBStatus     
        """
        amount = None
        
        try:
            se = self.Session()
            amount = se.query(Activity).count()
            se.close()
        except:
            logging.error("Counting activities not possible")
        finally:
            se.close()
            
        return amount 

    def addActivity(self,na):
        """ Insert an activity in the activity database
        As this method should later be used as a webservice
        the activities have to be serialized; we cannot
        use objects as parameters 
        OLD: insertActivity
        """
        md5 = None
               
        #if not DEBUG and na['user_id'] not in getUtility(IRegistry).forInterface(IAstreamSettings).blacklist:
        if not DEBUG:
            md5 = hashlib.new('md5', str(na) + str(datetime.now())   ).hexdigest()

            a = Activity(
                md5             = md5,
                user_id         = na['user_id'],
                user_name       = na['user_name'],
                user_email      = na['user_email'],
                content_uid     = na['content_uid'],
                content_title   = na['content_title'],
                content_path    = na['content_path'],
                message         = na['message'],
                timestamp       = datetime.now()
                )
            try:
                se = self.Session()
                se.add(a)
                se.commit()
                se.close()
            except:
                logging.error("Could not insert %s" % str(a))
            finally:
                se.close()
            
        return md5

    def getActivityComments(self, activity_md5, max=50, offset=0):
        """ return the latest MAX activities
        OLD: getActivityComments
        """
        if max > 50: max = 50 # never > 50 !
        
        comments = None
        
        try:
            se = self.Session()
            a = se.query(Activity).filter(Activity.md5 == activity_md5).one()
            comments = a.comments
            se.close()
        except:
            logging.error("Retrieving comment wit %s not possible" % activity_md5)
        finally:
            se.close()

        if comments:
            db_utils = DBUtils()                
            return [  db_utils.convertAttributesToDict(comment) for comment in comments   ]

    def getComments(self, timestamp=None, newer=True, order_field="id", descending=True, user_id="", max=50, offset=0):
        """ returns  comments
        """
        comments = None
        if max > 50: max = 50 # never > 50 !

        se = self.Session()
        q = se.query(Comment)
        
        if user_id:
            q = q.filter(Comment.user_id == user_id)
        if timestamp:
            if newer:
                q = q.filter(Comment.timestamp > timestamp)
            else:
                q = q.filter(Comment.timestamp < timestamp)
                
        if order_field and descending:
            q = q.order_by(desc(getattr(Comment,order_field)))
                
        comments = q[offset:offset+max]

        se.close()
        return comments

    def addComment(self,nc):
        """ Insert an comment to the activity in the database
            Comment is a dict (nc: new comment)
            nc must be a dict because this method will
            be part of a webservice
            OLD: insertActivityComment
        """
                
        md5 = hashlib.new('md5', str(nc) + str(datetime.now())).hexdigest()
        timestamp = datetime.now()
        
        c = Comment(
                activity_md5    = nc['activity_md5'],
                user_id         = nc['user_id'],
                user_name       = nc['user_name'],
                user_email      = nc['user_email'],
                comment         = nc['comment'],
                timestamp       = timestamp,
                md5             = md5                
            )

        se = self.Session()
        a = se.query(Activity).filter(Activity.md5 == c.activity_md5).one()
        a.comments.append(c)
        se.commit()
        se.close()
            
        return { 'md5':md5, 'timestamp': str(timestamp) }

    def updateComment(self,md5,new_comment):
        """ updates an existing comment in the database
            Comment is a dict (nc: new comment)
            nc must be a dict because this method will
            be part of a webservice
            OLD: insertActivityComment
        """
        
        comment = None
        timestamp = datetime.now()    
        se = self.Session()
        c = se.query(Comment).filter(Comment.md5 == md5).one()
        comment = c.comment + '\n' + new_comment['comment']
        
        md5 = c.md5
        c.comment = comment
        c.timestamp = timestamp
                
        se.commit()            
        se.close()

        return { 'md5':md5, 'timestamp': str(timestamp) }    

    def getLatestActivityComment(self,activity_md5):
        """ Returns the latest comment to the activity, if any
        """     
        if not activity_md5:
            logging.warn("getLatestActivityComment: MD5 Key of the latest activity is missing.")
            return False
           
        c = None
        try:
            se = self.Session()
            a = se.query(Activity).filter(Activity.md5 == activity_md5).one()
            c = a.comments[-1]
            se.close()
        except:
            logging.info("First comment to %s " % activity_md5)
        finally:
            se.close()
            
        db_utils = DBUtils()
        if c:
            return db_utils.convertAttributesToDict(c)
        else:
            return False

class DBUtils():
    """ Help functions
    """        
    def convertAttributesToDict(self, object):
        """Returns all public attributes of an object as a dict of attributes"""
        adict = dict((key, value) for key, value in object.__dict__.iteritems() 
                   if not callable(value) and not key.startswith('_'))
            
        return adict

