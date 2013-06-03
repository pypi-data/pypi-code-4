################################################################
# vs.org (C) 2011, Veit Schiele
################################################################

# $Id$

from zope.interface import Interface
# -*- Additional Imports Here -*-
from zope import schema

from vs.org import orgMessageFactory as _



class IBase(Interface):
    """Common elements for other contenttypes"""

    # -*- schema definition goes here -*-
    image = schema.Bytes(
        title=_(u"label_image"),
        required=False,
        description=_(u"help_image"),
    )

    url = schema.TextLine(
        title=_(u"label_url"),
        required=False,
        description=_(u"label_url"),
    )
#
    email = schema.TextLine(
        title=_(u"label_email"),
        required=False,
        description=_(u"help_email"),
    )
#
    telephone = schema.TextLine(
        title=_(u"label_telephone"),
        required=False,
        description=_(u"help_telephone"),
    )
#
