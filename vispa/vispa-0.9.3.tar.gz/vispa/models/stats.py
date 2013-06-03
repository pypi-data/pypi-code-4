# -*- coding: utf-8 -*-

# imports
import time
from datetime import date
from sqlalchemy import Column, schema
from sqlalchemy.types import Unicode, Integer, Date
from vispa.models import Base


class AccessStats(Base):

    __tablename__  = 'access_statistics'
    user_ip        = Column(Unicode(60), nullable=False, primary_key=True)
    user_agent     = Column(Unicode(200), nullable=False, primary_key=True)
    date           = Column(Date, nullable=False, default=date.today, primary_key=True)
    pis            = Column(Integer, nullable=False, default=0)
    __table_args__ = (schema.PrimaryKeyConstraint(user_ip, user_agent, date),)

    @staticmethod
    def click(session, ip, agent):
        # is there an entry, defined by (ip, agent, date)?
        row = session.query(AccessStats).filter_by(user_ip=ip, user_agent=agent, date=date.today()).first()
        if not isinstance(row, AccessStats):
            row = AccessStats(user_ip=ip, user_agent=agent)
            session.add(row)
            session.commit()
        row.pis += 1


class PageStats(Base):

    __tablename__  = 'page_statistics'
    page           = Column(Unicode(50), nullable=False, primary_key=True)
    date           = Column(Date, nullable=False, default=date.today, primary_key=True)
    pis            = Column(Integer, nullable=False, default=0)
    __table_args__ = (schema.PrimaryKeyConstraint(page, date),)

    @staticmethod
    def click(session, page):
        row = session.query(PageStats).filter_by(page=page, date=date.today()).first()
        if not isinstance(row, PageStats):
            row = PageStats(page=page)
            session.add(row)
            session.commit()
        row.pis += 1