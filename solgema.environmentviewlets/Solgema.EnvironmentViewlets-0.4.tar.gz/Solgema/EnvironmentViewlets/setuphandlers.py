from StringIO import StringIO

from Acquisition import aq_base
from Products.CMFCore.utils import getToolByName
from Products.CMFEditions import StandardModifiers
from Products.CMFEditions.VersionPolicies import ATVersionOnEditPolicy
from zope.publisher.interfaces.browser import IDefaultBrowserLayer

from AccessControl import ClassSecurityInfo
from zope.interface import implements
from Products.CMFCore import permissions
from zope.component import getUtility, getAdapters
from zope.component import getMultiAdapter
from zope.component import getSiteManager

from plone.portlets.interfaces import IPortletManager
security = ClassSecurityInfo()


from zope.interface.interfaces import IInterface
#from zope.interface.interfaces import InterfaceClass

from Products.CMFCore.permissions import ManagePortal
from plone.browserlayer import utils

from Solgema.EnvironmentViewlets import interfaces

#from Solgema.Immo.Extensions.install import setup_types

def setupSolgemaEnvironmentViewlets(context):
    """various things to do while installing..."""
    if context.readDataFile('solgemaenvironmentviewlets_various.txt') is None:
        return
    site = context.getSite()
    out = StringIO()
    sm = site.getSiteManager()

    print >> out, "Installing Solgema Environment Viewlets Settings Utility"

