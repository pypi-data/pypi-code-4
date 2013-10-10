# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
import logging


DEFAULT_DOORMAT_DOCUMENT_HTML = """<p>
This is the default doormat text.
Please go to /doormat/column-1/section-1/document/edit to edit it.
</p>"""
DEFAULT_DOORMAT_DOCUMENT_TITLE = "Document title"
logger = logging.getLogger('Doormat: setuphandlers')


def _tryInvokeFactory(folder, ptype, oid):
    """Returns an object (of portal_type ptype) with a specific id (oid) from
    a given folder.

    If it doesn't exist, create it.
    """
    if not hasattr(folder, oid):
        folder.invokeFactory(ptype, oid)
    else:
        # Note that we don't check if the existing object is of the correct
        # type. But then we'd have to use a new id, check if that exists, etc.
        pass
    return getattr(folder, oid)


def createDefaultContent(portal):
    doormat = _tryInvokeFactory(portal, 'Doormat', 'doormat')
    doormat.setTitle('Doormat')
    doormat.setExcludeFromNav(True)  # Don't show in portal sections
    doormat.reindexObject()
    column = _tryInvokeFactory(doormat, 'DoormatColumn', 'column-1')
    column.setTitle('Section 1')
    column.reindexObject()
    section = _tryInvokeFactory(column, 'DoormatSection', 'section-1')
    section.setTitle('Section 1')
    section.reindexObject()
    document = _tryInvokeFactory(section, "Document", 'document-1')
    if document.meta_type.startswith('Dexterity'):
        # A Dexterity-link
        document.text = DEFAULT_DOORMAT_DOCUMENT_HTML
        document.title = DEFAULT_DOORMAT_DOCUMENT_TITLE
    else:
        document.setText(DEFAULT_DOORMAT_DOCUMENT_HTML)
        document.setTitle(DEFAULT_DOORMAT_DOCUMENT_TITLE)


def removeContent(context):
    portal = context.getSite()
    # Usually this should be enough
    if hasattr(portal, 'doormat'):
        portal.manage_delObjects(['doormat'])
    catalog = getToolByName(portal, 'portal_catalog')
    # Remove _everything_.
    for ptype in ['DoormatReference', 'DoormatCollection', 'DoormatMixin',
                  'DoormatSection', 'DoormatColumn', 'Doormat']:
        for brain in catalog(portal_type=ptype):
            obj = brain.getObject()
            obj.aq_parent.manage_delObjects(brain.getId)


def isNotDoormatProfile(context):
    return context.readDataFile("Doormat_marker.txt") is None


def setupVarious(context):
    if isNotDoormatProfile(context):
        return
    portal = context.getSite()
    createDefaultContent(portal)
