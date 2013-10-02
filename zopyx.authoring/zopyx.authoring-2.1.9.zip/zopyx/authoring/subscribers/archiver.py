#####################################################################
# zopyx.authoring
# (C) 2011, ZOPYX Limited, D-72070 Tuebingen. All rights reserved
#####################################################################

from DateTime import DateTime
from Products.CMFCore.utils import getToolByName

def archiver(event):
    """ Archiver """

    conversion = event.conversion
    wf_tool = getToolByName(conversion, 'portal_workflow')

    archive_folder = conversion.getArchiveFolder()
    if archive_folder is None:
        return # nothing to do

    # items to be archived?
    publication_folder = conversion.getPublicationsFolder()
    ids = publication_folder.objectIds()
    if not ids:
        return

    # determine presets for archive folder
    content_folder = conversion.restrictedTraverse(conversion.getContentFolderPath())
    content_folder_id = content_folder.getId()
    content_folder_title = content_folder.Title()

    if not content_folder_id in archive_folder.objectIds():
        archive_folder.invokeFactory('Folder', 
                                     id=content_folder_id, 
                                     title=content_folder_title)
        wf_tool.doActionFor(archive_folder[content_folder_id] , 'publish')
        archive_folder[content_folder_id].reindexObject()

    # create a new folder with timestamp as ID
    content_archive_folder = archive_folder[content_folder_id]
    now = DateTime()
    dest_id= now.strftime('%Y%m%dT%H%M%S')
    dest_title = 'Version (%s)' % now.strftime('%d.%m.%Y-%H:%Mh')
    content_archive_folder.invokeFactory('Folder', id=dest_id, title=dest_title) 
    wf_tool.doActionFor(content_archive_folder[dest_id] , 'publish')
    content_archive_folder[dest_id].reindexObject()

    # move new folder to the top
    content_archive_folder.moveObjectToPosition(dest_id, 0)

    # cut/paste from publication folder to archive folder
    dest_folder = content_archive_folder[dest_id]
    dest_folder.manage_pasteObjects(publication_folder.manage_cutObjects(ids))

    # add (Version: XXXX) to archived image content 
    for id in dest_folder.objectIds():
        ob = dest_folder[id]
        if ob.portal_type in ('Image',):
            ob.setTitle('%s (%s)' % (ob.Title(), dest_title))
            ob.reindexObject()


