# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
from Products.statusmessages.interfaces import IStatusMessage
from plone.memoize.view import memoize
from redturtle.sqlcontents import sqlcontentsLogger as logger, \
    sqlcontentsMessageFactory as _, sqlcontentsLogger
from redturtle.sqlcontents.adapters.engine import ISQLFolderEngine


class View(BrowserView):
    '''
    The view for SQLQuery objects
    '''
    def __init__(self, context, request):
        '''
        We need also the engine, taken from the adapted parent
        '''
        super(View, self).__init__(context, request)
        self.execute
        self.sqlkeys
        self.sqlrows

    @memoize
    def declareEncodingProblem(self):
        '''
        Declare we have an encoding problem logging the exception

        We put this in a memoized method to have it onece for request
        '''
        msg = 'Encoding problem %s' % self.context.UID()
        sqlcontentsLogger.exception(msg)

    def safedisplay(self, value):
        '''
        Takes value and tries to convert it in utf8 for injecting it in the
        template
        '''
        if value is None:
            return u''
        try:
            if not isinstance(value, unicode):
                value = str(value)
            return unicode(value)
        except:
            self.declareEncodingProblem()
            return u''

    @property
    @memoize
    def sqlengine(self):
        '''
        We take the parent of this object and then adapt it
        '''
        return ISQLFolderEngine(self.context.aq_inner.aq_parent)

    @property
    @memoize
    def sqlkeys(self):
        '''
        Get the keys (the column ids)
        '''
        if not self.sqlstatus:
            return ()
        return self.execute.keys()

    @property
    @memoize
    def column_names_map(self):
        '''
        Create a mapping between known column ids and names
        '''
        names_map = {}
        for data_grid_line in self.context.getColumn_names():
            key, value = data_grid_line['key'], data_grid_line['value']
            names_map[key] = value
        return names_map

    @property
    @memoize
    def column_names(self):
        '''
        Translate, if possible the column ids in to human readable names
        If no value is given return the key a s default
        '''
        names = []
        names_map = self.column_names_map
        for key in self.sqlkeys:
            names.append(names_map.get(key, key))
        return names

    @property
    @memoize
    def sqlrows(self):
        '''
        Get the keys (the column ids)
        '''
        if not self.sqlstatus:
            return ()
        return self.execute.fetchall()

    def on_error(self):
        '''
        What to do in case of error
        '''
        self.sqlstatus = False
        msg = _("Error executing query")
        logger.exception(msg)
        sm = IStatusMessage(self.request)
        sm.addStatusMessage(msg, 'error')

    @property
    @memoize
    def execute(self):
        '''
        This executes the SQLQuery query with the engine
        '''
        self.sqlstatus = True
        try:
            return self.sqlengine.execute(self.context.getQuery())
        except:
            self.on_error()
