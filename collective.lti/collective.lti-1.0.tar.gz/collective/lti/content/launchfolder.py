from zope.interface import implements
from Products.ATContentTypes.atct import ATFolder, ATFolderSchema
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from collective.lti.interfaces import ILaunchFolder
from Products.ATContentTypes.content.base import registerATCT
from collective.lti.config import PROJECTNAME


LaunchFolderSchema = ATFolderSchema.copy()
finalizeATCTSchema(LaunchFolderSchema)

class LaunchFolder(ATFolder):
    '''
    Folder for containing LTI launch information
    '''
    
    implements(ILaunchFolder)
    schema = LaunchFolderSchema
    portal_type = 'LaunchFolder'

    _at_rename_after_creation = True


registerATCT(LaunchFolder, PROJECTNAME)
