#! /usr/bin/env python
# -*- coding: utf-8 -*-

import logging
log = logging.getLogger(__name__)

from cement.core import hook

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from sqlalchemy import Integer, Column, Enum, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.schema import Table

from datetime import datetime

Base = declarative_base()

class WorkLog(Base):
    __tablename__ = 'worklog'

    id = Column(Integer, primary_key=True)
    activity = Column(Enum('start', 'end', 'resume'))
    description = Column(String(256)) # in case of start activity, this will be the activity name
    created_at = Column(DateTime(), default=datetime.now)
    start_attrs = relationship("StartAttrs", uselist=False, backref="worklog")

    def __unicode__(self):
        return "%s %s %s" % (self.created_at, self.activity.ljust(6), self.description)

    @staticmethod
    def iterate(fsm, session):
        q = session.query(WorkLog).order_by(WorkLog.created_at.desc()).all()

        while fsm.continue_():
            fsm.got(q.pop(0))

        return fsm.result()

class StartAttrs(Base):
    __tablename__ = 'start_attrs'

    id = Column(Integer, primary_key=True)
    worklog_id = Column(Integer, ForeignKey('worklog.id'))
    project = Column(String(256))
    ref = Column(Integer)

def init(db_url):
    e = create_engine(db_url)
    session = scoped_session(sessionmaker(bind=e, autoflush=True))

    Base.metadata.bind = e
    return session
