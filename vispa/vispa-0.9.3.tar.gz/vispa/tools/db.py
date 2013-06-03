# -*- coding: utf-8 -*-

# Imports
import cherrypy

__all__ = ['SATool']

class SATool(cherrypy.Tool):

    def __init__(self):
        """
        The SA tool is responsible for associating a SA session
        to the SA engine and attaching it to the current request.
        Since we are running in a multithreaded application,
        we use the scoped_session that will create a session
        on a per thread basis so that you don't worry about
        concurrency on the session object itself.
 
        This tools binds a session to the engine each time
        a requests starts and commits/rollbacks whenever
        the request terminates.
        """
        cherrypy.Tool.__init__(self, 'before_handler', self.bind_session, priority=60)
 
    def _setup(self):
        cherrypy.Tool._setup(self)
        cherrypy.request.hooks.attach('before_finalize', self.commit_transaction, priority=40)
 
    def bind_session(self):
        """
        Attaches a session to the request's scope by requesting
        the SA plugin to bind a session to the SA engine.
        """
        session = cherrypy.engine.publish('bind_session').pop()
        cherrypy.request.db = session
 
    def commit_transaction(self):
        """
        Commits the current transaction or rolls back
        if an error occurs. Removes the session handle
        from the request's scope.
        """
        if hasattr(cherrypy.request, 'db'):
            cherrypy.request.db = None
            cherrypy.engine.publish('commit_session')
 
