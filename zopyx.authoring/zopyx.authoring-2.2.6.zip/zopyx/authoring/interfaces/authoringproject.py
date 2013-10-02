from zope import schema
from zope.interface import Interface

try:
    from zope.app.container.constraints import contains
    from zope.app.container.constraints import containers
except ImportError:
    from zope.container.constraints import contains
    from zope.container.constraints import containers

from zopyx.authoring import authoringMessageFactory as _

class IAuthoringProject(Interface):
    """Authoring Project"""
    
    # -*- schema definition goes here -*-
