### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2008-2009 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################


from persistent import Persistent
from persistent.dict import PersistentDict
import sqlalchemy
from sqlalchemy.orm import scoped_session, sessionmaker, class_mapper
from threading import local

# import Zope3 interfaces
from zope.security.interfaces import NoInteraction

# import local interfaces
from ztfy.alchemy.interfaces import IAlchemyEngineUtility

# import Zope3 packages
from zope.container.contained import Contained
from zope.interface import implements
from zope.component import adapter, getUtility
from zope.publisher.interfaces import IEndRequestEvent
from zope.schema.fieldproperty import FieldProperty

# import local packages
from ztfy.alchemy.datamanager import ZopeTransactionExtension, join_transaction, \
                                     _SESSION_STATE, STATUS_ACTIVE, STATUS_READONLY
from ztfy.utils.request import getRequest, getRequestData, setRequestData


class AlchemyEngineUtility(Persistent):
    """A persistent utility providing a database engine"""

    implements(IAlchemyEngineUtility)

    name = FieldProperty(IAlchemyEngineUtility['name'])
    dsn = FieldProperty(IAlchemyEngineUtility['dsn'])
    echo = FieldProperty(IAlchemyEngineUtility['echo'])
    pool_size = FieldProperty(IAlchemyEngineUtility['pool_size'])
    pool_recycle = FieldProperty(IAlchemyEngineUtility['pool_recycle'])
    register_geotypes = FieldProperty(IAlchemyEngineUtility['register_geotypes'])
    register_opengis = FieldProperty(IAlchemyEngineUtility['register_opengis'])
    encoding = FieldProperty(IAlchemyEngineUtility['encoding'])
    convert_unicode = FieldProperty(IAlchemyEngineUtility['convert_unicode'])

    def __init__(self, name=u'', dsn=u'', echo=False, pool_size=25, pool_recycle=-1, register_geotypes=False, register_opengis=False, encoding='utf-8', convert_unicode=False, **kw):
        self.name = name
        self.dsn = dsn
        self.encoding = encoding
        self.convert_unicode = convert_unicode
        self.echo = echo
        self.pool_size = pool_size
        self.pool_recycle = pool_recycle
        self.register_geotypes = register_geotypes
        self.register_opengis = register_opengis
        self.kw = PersistentDict()
        self.kw.update(kw)

    def __setattr__(self, name, value):
        super(AlchemyEngineUtility, self).__setattr__(name, value)
        if (name != '_v_engine') and hasattr(self, '_v_engine'):
            delattr(self, '_v_engine')

    def getEngine(self):
        engine = getattr(self, '_v_engine', None)
        if engine is not None:
            return engine
        kw = {}
        kw.update(self.kw)
        self._v_engine = sqlalchemy.create_engine(str(self.dsn),
                                                  echo=self.echo,
                                                  pool_size=self.pool_size,
                                                  pool_recycle=self.pool_recycle,
                                                  encoding=self.encoding,
                                                  convert_unicode=self.convert_unicode,
                                                  strategy='threadlocal', **kw)
        if self.register_geotypes:
            try:
                import psycopg2
                import psycopg2.extensions as psycoext
                from GeoTypes import initialisePsycopgTypes
                url = self._v_engine.url
                initialisePsycopgTypes(psycopg_module=psycopg2,
                                       psycopg_extensions_module=psycoext,
                                       connect_string='host=%(host)s port=%(port)s dbname=%(dbname)s user=%(user)s password=%(password)s' % \
                                                      { 'host': url.host,
                                                        'port': url.port,
                                                        'dbname': url.database,
                                                        'user': url.username,
                                                        'password': url.password },
                                       register_opengis_types=self.register_opengis)
            except:
                pass
        return self._v_engine

    def _resetEngine(self):
        engine = getattr(self, '_v_engine', None)
        if engine is not None:
            engine.dispose()
            self._v_engine = None


class PersistentAlchemyEngineUtility(AlchemyEngineUtility, Contained):
    """A persistent implementation of AlchemyEngineUtility stored into ZODB"""


def getEngine(engine):
    if isinstance(engine, (str, unicode)):
        engine = getUtility(IAlchemyEngineUtility, engine).getEngine()
    return engine


class SessionsStorage(local):
    """Thread local sessions storage"""

    engines = {}

    def clear(self):
        self.engines.clear()

sessions = SessionsStorage()


def getSession(engine, join=True, status=STATUS_ACTIVE, request=None):
    """Get a new SQLAlchemy session
    
    Session is stored in request and in a sessions storage"""
    session = None
    if request is None:
        try:
            request = getRequest()
        except NoInteraction:
            pass
    if request is not None:
        session_data = getRequestData('ztfy.alchemy.session', request, {})
        session = session_data.get(engine)
    if session is None:
        _engine = getEngine(engine)
        if _engine in sessions.engines:
            session = sessions.engines[_engine]
            if status != STATUS_READONLY:
                _SESSION_STATE[id(session)] = status
        if session is None:
            factory = scoped_session(sessionmaker(bind=_engine, twophase=True, extension=ZopeTransactionExtension()))
            session = factory()
            if join:
                join_transaction(session, initial_state=status)
            sessions.engines[engine] = session
        if (request is not None) and (session is not None):
            session_data[engine] = session
            setRequestData('ztfy.alchemy.session', session_data, request)
    return session


def getUserSession(engine, status=STATUS_ACTIVE, request=None):
    """Shortcut function to get user session"""
    if isinstance(engine, basestring):
        session = getSession(engine, status=status, request=request)
    else:
        session = engine
    return session


@adapter(IEndRequestEvent)
def handleEndRequest(event):
    """Clear thread's sessions on request end"""
    sessions.clear()


class MetadataManager(object):
    """A manager for metadata management, to be able to use the same table name
    in different databases
    """

    def __init__(self):
        self.metadata = {}

    def getTable(self, engine, table, fallback):
        md = self.metadata.get(engine)
        if md and table in md.tables:
            return md.tables[table]
        if fallback and engine:
            md = self.metadata.get('')
        if md and table in md.tables:
            return md.tables[table]
        return None

    def __call__(self, engine=''):
        md = self.metadata.get(engine)
        if md is None:
            md = self.metadata[engine] = sqlalchemy.MetaData()
        return md

metadata = MetadataManager()


_tableToEngine = {}
_classToEngine = {}

def _assignTable(table, engine, session=None):
    _table = metadata.getTable(engine, table, True)
    util = getUtility(IAlchemyEngineUtility, name=engine)
    if session is None:
        session = getSession(engine)
    session.bind_table(_table, util.getEngine())


def assignTable(table, engine, immediate=True):
    _tableToEngine[table] = engine
    if immediate:
        _assignTable(table, engine)


def _assignClass(class_, engine, session=None):
    _mapper = class_mapper(class_)
    util = getUtility(IAlchemyEngineUtility, name=engine)
    if session is None:
        session = getSession(engine)
    session.bind_mapper(_mapper, util.getEngine())


def assignClass(class_, engine, immediate=True):
    _classToEngine[class_] = engine
    if immediate:
        _assignClass(class_, engine)
