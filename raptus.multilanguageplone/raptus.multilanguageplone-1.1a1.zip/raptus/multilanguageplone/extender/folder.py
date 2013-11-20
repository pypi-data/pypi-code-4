from zope.component import adapts
try:
    from plone.app.folder.folder import ATFolder
except:
    from Products.ATContentTypes.content.folder import ATFolder

from base import DefaultExtender

class FolderExtender(DefaultExtender):
    adapts(ATFolder)