"""Simplified ORM abstraction module for Schevo""" 

from ._databaseproxy import DatabaseProxy, ConnectionError
from ._relation import RelationProxy

#XXX: AnonymousUser should be defined in blogengine.contrib.anonymoususer
#from models import AnonymousUser

from .schevo_compat import XdserverProxy

#Add basic session management stuff 
#from .sql import (
#    ScopedSession as scoped_session,
#    with_session
#    )

__all__ = [
    'DatabaseProxy',
    'RelationProxy', 
    'XdserverProxy',
    'ConnectionError',
    #'models', 
    'schevo_compat',
    #'AnonymousUser',
    #'scoped_session',
    #'with_session',
    #'with_schevo_database']
    ]    
