#
# Copyright 2008, Blue Dynamics Alliance, Austria - http://bluedynamics.com
#
# GNU General Public Licence Version 2 or later

__author__ = """Robert Niederreiter <rnix@squarewave.at>"""
__docformat__ = 'plaintext'

from zope.interface import Interface
from zope.schema import TextLine
from zope.configuration.fields import GlobalObject
from zope.configuration.fields import Tokens

class IHotspotDirective(Interface):
    
    name = TextLine(
        title=u"The name of this hotspot",
        description=u"",
        required=True)
    
    obj = GlobalObject(
        title=u"The object this hotspot applies",
        description=u"",
        required=False)
    
    interface = GlobalObject(
        title=u"The interface this hotspot applies",
        description=u"",
        required=False)
    
    resource = TextLine(
        title=u"The resources this hotspot applies",
        description=u"",
        required=False)
    
    considerparams = Tokens(
        title=u"Request params to consider",
        description=u"",
        required=False,
        value_type=TextLine())
