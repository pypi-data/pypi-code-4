from Products.Archetypes.utils import shasattr, isFactoryContained
from Products.CMFCore.utils import getToolByName
from Products.Archetypes.config import CATALOGMAP_USES_PORTALTYPE, TOOL_NAME
from Products.CMFPlone.Portal import PloneSite
from Products.Archetypes import config as archetypes_config
from Acquisition import aq_base, aq_parent, aq_inner

from zope.interface import implements

from plone.uuid.interfaces import IUUID

from Products.Archetypes.exceptions import ReferenceException
from Products.Archetypes.interfaces import IReferenceable
from Products.Archetypes.utils import shasattr, isFactoryContained,getRelURL

from OFS.ObjectManager import BeforeDeleteException

from OFS.CopySupport import CopySource
from OFS.Folder import Folder

from App.class_init import InitializeClass
from AccessControl import ClassSecurityInfo

from Products.Archetypes.Schema import Schemata

def indexObject(self):
    if isFactoryContained(self):
        return
    catalogs = getCatalogs(self)
    url = '/'.join(self.getPhysicalPath())
    for c in catalogs:
        if c:
            c.catalog_object(self, url)

def unindexObject(self):
    if isFactoryContained(self):
        return
    catalogs = getCatalogs()
    url = '/'.join(self.getPhysicalPath())
    for c in catalogs:
        if c._catalog.uids.get(url, None) is not None:
            c.uncatalog_object(url)

def getCatalogs(self):
    pc = getToolByName(self,'portal_catalog', None)
    uc = getToolByName(self,'uid_catalog', None)

    return [pc,uc]

def UID(self):
    """ """
    return getattr(self,'_at_uid',None)

PloneSite.UID=UID
PloneSite.getUID=UID

def addReference(self, object, relationship=None, referenceClass=None,
                 updateReferences=True, **kwargs):
    tool = getToolByName(self, 'reference_catalog')
    return tool.addReference(self, object, relationship, referenceClass,
                             updateReferences, **kwargs)

PloneSite.addReference=addReference

def _getReferenceAnnotations(self):
    # given an object, extract the bag of references for which it is the
    # source
    if not getattr(aq_base(self), archetypes_config.REFERENCE_ANNOTATION, None):
        setattr(self, archetypes_config.REFERENCE_ANNOTATION,
                Folder(archetypes_config.REFERENCE_ANNOTATION))
    return getattr(self, archetypes_config.REFERENCE_ANNOTATION).__of__(self)

PloneSite._getReferenceAnnotations=_getReferenceAnnotations

def Schema(self):
    return Schemata()

PloneSite.Schema=Schema


