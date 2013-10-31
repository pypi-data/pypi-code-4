#
# Copyright 2008, Blue Dynamics Alliance, Austria - http://bluedynamics.com
#
# GNU General Public Licence Version 2 or later

__author__ = """Robert Niederreiter <rnix@squarewave.at>"""
__docformat__ = 'plaintext'

from zope.configuration.exceptions import ConfigurationError

try:
    from zope.component.zcml import utility
except:
    # BBB
    from zope.app.component.metaconfigure import utility

from interfaces import IHotspot
from hotspot import Hotspot

def hotspotDirective(_context, name, obj=None, interface=None,
                     resource=[], considerparams=[]):
    if not obj and not interface and not resource:
        raise ConfigurationError(u"Du solltest dich entscheiden, Jonny!")
    hotspot = Hotspot(obj, interface, resource, considerparams)
    utility(_context,
            provides=IHotspot,
            component=hotspot,
            name=name)
