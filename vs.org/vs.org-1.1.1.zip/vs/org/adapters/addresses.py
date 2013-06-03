################################################################
# vs.org (C) 2011, Veit Schiele
################################################################

# $Id$

from zope.interface import implements
from ..interfaces import IAddressProvider

class InstitutionAddresses(object):
    """ 
    Adapt an institution to address data
    """

    implements(IAddressProvider)

    def __init__(self, context):
        self.context = context

    def getAddresses(self):
        """ """
        result = []
        for address in self.context.getAddresses():
            if address['street']:
                result.append( {
                    'title': "%s, %s %s" % (address['street'], address['zipCode'], address['city']), 
                    'geocode': address['geocode'] and [float(i.strip()) 
                                                       for i in address['geocode'].split(',')] or [],
                })
        return result
