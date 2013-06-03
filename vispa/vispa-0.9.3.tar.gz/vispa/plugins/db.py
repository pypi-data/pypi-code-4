# -*- coding: utf-8 -*-

# imports
import cherrypy
from cherrypy.process.plugins import SimplePlugin
from cherrypy.process import wspbus
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from vispa.models import Base


class SAPlugin(SimplePlugin):

    def __init__(self, bus, identifier):
        """
        The plugin is registered to the CherryPy engine and therefore
        is part of the bus (the engine *is* a bus) registery.
        We use this plugin to create the SA engine. At the same time,
        when the plugin starts we create the tables into the database
        using the mapped class of the global metadata.
        """
        SimplePlugin.__init__(self, bus)
        self.bus.listeners.setdefault('bind_session', set())
        self.bus.listeners.setdefault('commit_session', set())

        self._engine = None
        self._session = scoped_session(sessionmaker(autoflush=True, autocommit=False))
        self._identifier = identifier

    def start(self):
        self._engine = create_engine(self._identifier, echo=False)
        self._create_all()

    def stop(self):
        if self._engine:
            self._engine.dispose()
            del self._engine

    def bind_session(self):
        """
        Whenever this plugin receives the 'bind-_session' command, it applies
        this method and to bind the current _session to the engine.
        It then returns the _session to the caller.
        """
        self._session.configure(bind=self._engine)
        return self._session

    def commit_session(self):
        """
        Commits the current transaction or rollbacks if an error occurs.
        In all cases, the current _session is unbound and therefore
        not usable any longer.
        """
        try:
            self._session.commit()
        except:
            self._session.rollback()
        finally:
            self._session.remove()

    def _create_all(self):
        self.bus.log('Creating database')
        from vispa.models.user import User
        from vispa.models.profile import Profile
        from vispa.models.workspace import Workspace
        from vispa.models.stats import AccessStats, PageStats
        from vispa.models.preference import VispaPreference
        Base.metadata.create_all(self._engine)

    def _destroy_all(self):
        self.bus.log('Destroying database')
        Base.metadata.drop_all(self._engine)
