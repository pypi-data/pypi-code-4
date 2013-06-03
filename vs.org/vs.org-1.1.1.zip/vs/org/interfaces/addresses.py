################################################################
# vs.org (C) 2011, Veit Schiele
################################################################

# $Id$

from zope.interface import Interface

class IAddressProvider(Interface):
    """ Marker interface for an address provider """

    def getAddresses(self):
        """ Addresses to be displayed  """
