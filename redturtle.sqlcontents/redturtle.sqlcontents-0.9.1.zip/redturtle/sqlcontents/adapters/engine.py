# -*- coding: utf-8 -*-
from sqlalchemy import create_engine
from zope.interface import Interface


class ISQLFolderEngine(Interface):
    '''
    Interface for getting an Engine from a SQLFolder
    '''


class SQLFolderEngine(object):
    '''
    Adapts a SQLFolder to have an engine
    '''
    def __init__(self, context):
        '''
        @param context: An object implementing ISQLFolder
        '''
        self.context = context
        self.engine = self.getEngine()

    def getEngine(self):
        '''
        Let's get the engine through SQLAlchemy

        The connection_url has to be taken avoiding the accessor to
        overcome the security constraints on getConnection_url
        '''
        field = self.context.getField('connection_url')
        connection_url = field.get(self.context)
        return create_engine(connection_url)

    def execute(self, query):
        '''
        Execute the query we are passing
        '''
        return self.engine.execute(query)
