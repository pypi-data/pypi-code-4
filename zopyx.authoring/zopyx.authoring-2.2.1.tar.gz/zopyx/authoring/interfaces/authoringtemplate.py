from zope import schema
from zope.interface import Interface

try:
    from zope.app.container.constraints import contains
    from zope.app.container.constraints import containers
except:
    from zope.container.constraints import contains
    from zope.container.constraints import containers

from zopyx.authoring import authoringMessageFactory as _

class IAuthoringTemplate(Interface):
    """Authoring Template"""
    
    # -*- schema definition goes here -*-
