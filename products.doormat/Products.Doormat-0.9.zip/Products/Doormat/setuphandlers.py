# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
import logging


DEFAULT_DOORMAT_DOCUMENT_HTML = """<p>
This is the default doormat text.
Please go to /doormat/column-1/section-1/document/edit to edit it.
</p>"""
DEFAULT_DOORMAT_DOCUMENT_TITLE = "Document title"
logger = logging.getLogger('Doormat: setuphandlers')


def createDefaultContent(portal):
    portal.invokeFactory('Doormat', 'doormat')
    doormat = portal.doormat
    doormat.setTitle('Doormat')
    doormat.setExcludeFromNav(True)  # Don't show in portal sections
    doormat.reindexObject()
    doormat.invokeFactory('DoormatColumn', 'column-1')
    column = getattr(doormat, 'column-1')
    column.setTitle('Section 1')
    column.reindexObject()
    column.invokeFactory('DoormatSection', 'section-1')
    section = getattr(column, 'section-1')
    section.setTitle('Section 1')
    section.reindexObject()
    section.invokeFactory("Document", 'document-1')
    document = getattr(section, 'document-1')
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
