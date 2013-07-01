from zope import schema
from zope.interface import Interface

from zope.app.container.constraints import contains
from zope.app.container.constraints import containers

from raptus.header import headerMessageFactory as _

class IHeader(Interface):
    """This header will display all contained images on top of your site"""
    
    # -*- schema definition goes here -*-
