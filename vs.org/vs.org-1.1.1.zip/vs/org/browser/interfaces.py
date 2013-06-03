# -*- coding: utf-8 -*-

################################################################
# vs.org (C) 2011, Veit Schiele
################################################################

# $Id$

from zope.interface import Interface

class IStaffSortView(Interface):
    """ StaffSortView
    """
    def getSortedStaff(self):
        """
        """
class IImageView(Interface):
    """ Image - View
    """
    def tag(self,fieldid=None,scale=None, height=None, width=None, alt=None,css_class=None, title=None, **kwargs):
        """
        """
    def getImageSize(self, fieldid=None, scale=None):
        """
        """

class IOrganisation(Interface):
    """
    """
    def getInstitutionOverview(self):
        """
        """
    def getDepartmentOverview(self):
        """
        """

class IVCardView(Interface):

    def vcard(self, **kwargs):
        pass

class IMapView(Interface):
    """ Google Maps view  """

    def getAddresses(self):
        """ Addresses to be displayed  """

class IVBBView(Interface):
    """ VBB - Link
    """
    def getVBBUrl(self):
        """
        """

