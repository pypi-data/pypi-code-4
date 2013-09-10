#-*- coding: utf-8 -*-
import sqlahelper
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import String, Integer, Text, Enum
from sqlalchemy.ext.hybrid import hybrid_property
import hashlib
import random
from sqlalchemy.orm import relationship
from pyramid_rest.models_crud import constructSuperModel, CRUD

Base = sqlahelper.get_base()

USER_GROUPS = ["main",
               "admin",
               "new",
               "banned"]


class Users(Base, CRUD):
    __tablename__ = "_rest_users"
    id = Column(Integer, primary_key = True)
    type = Column(String(200))
    __mapper_args__ = {'polymorphic_identity': '_rest_users',
                       'polymorphic_on': type}
    
    email = Column(String(200), unique = True)
    group = Column(Enum(*USER_GROUPS, name = "user_groups"), default = "new")
    
    _password = Column(String(100))
    
    @hybrid_property
    def password(self):
        return self._password
    
    @password.setter
    def _set_password(self, value):
        self._password = hashlib.sha256(str(value)).hexdigest()
    
    def check_password(self, value):
        return (self._password == hashlib.sha256(value).hexdigest())
    
    def add_session(self):
        db_session = Sessions()._add()
        self.sessions += [db_session]
        return db_session
    
    def logout(self):
        self.sessions = []
        
    def __init__(self, *a, **k):
        Base.__init__(self, *a, **k)


@constructSuperModel  
class Sessions(Base):
    __tablename__ = "sessions"
    id = Column(Integer, primary_key = True)
    user_id = Column(Integer, ForeignKey("_rest_users.id", ondelete = "cascade"))
    sid = Column(String(200), unique = True)
    
    user = relationship(Users, backref = "sessions")
    
    def __init__(self, *a, **k):
        k["sid"] = hashlib.sha256(str(random.randrange(10, 10**100))).hexdigest()
        Base.__init__(self, *a, **k)
    

    
    
    
    
    