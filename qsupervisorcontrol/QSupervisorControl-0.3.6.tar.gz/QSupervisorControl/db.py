# -*- coding: utf-8 -*-
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import sqlalchemy
import os


def get_engine():
    dbfile = os.path.sep.join([os.environ.get('HOME'), '.config', 'qsc.dat'])
    old_dbfile = os.path.sep.join([os.environ.get('HOME'), 'qsc.dat'])

    if os.path.exists(old_dbfile) is True:
        print('move old configuration for new destination %s' % old_dbfile)
        src_fd = open(old_dbfile, 'rb')
        dst_fd = open(dbfile, 'wb')

        dst_fd.write(src_fd.read())
        dst_fd.close()
        src_fd.close()

        os.unlink(old_dbfile)

    print('database file %s' % dbfile)

    return sqlalchemy.create_engine(
        'sqlite:///%s' % dbfile,
        native_datetime=True,
        echo=False
    )


def get_session():
    Session = sessionmaker()
    Session.configure(bind=get_engine())

    return Session()

Base = declarative_base()


class Launche(Base):

    __tablename__ = 'launche'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    name = sqlalchemy.Column(sqlalchemy.String)
    monitor_pattern = sqlalchemy.Column(sqlalchemy.String)
    touch_file = sqlalchemy.Column(sqlalchemy.String)
    log_file = sqlalchemy.Column(sqlalchemy.String)
    path = sqlalchemy.Column(sqlalchemy.String)

    def __init__(self, name, monitor_pattern=None):
        self.name = name
        self.monitor_pattern = monitor_pattern

Base.metadata.create_all(get_engine())
