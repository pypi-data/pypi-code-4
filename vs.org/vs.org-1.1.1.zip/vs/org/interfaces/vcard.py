################################################################
# vs.org (C) 2011, Veit Schiele
################################################################

# $Id$

from zope.interface import Interface


class IVCardData(Interface):

    def getVCardData():
        """ return vcard data """
