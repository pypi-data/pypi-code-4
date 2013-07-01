"""Definition of the Header content type
"""

from zope.interface import implements, directlyProvides

from Products.Archetypes import atapi
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content import schemata

from raptus.header import headerMessageFactory as _
from raptus.header.interfaces import IHeader
from raptus.header.config import PROJECTNAME

HeaderSchema = folder.ATFolderSchema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-

))

"""hidden not used schema fields"""
for field in ('excludeFromNav','creators','allowDiscussion','contributors','location','language', 'nextPreviousEnabled', 'rights' ):
    if HeaderSchema.has_key(field):
        HeaderSchema[field].widget.visible = {'edit': 'invisible', 'view': 'invisible'}

# Set storage on fields copied from ATFolderSchema, making sure
# they work well with the python bridge properties.

HeaderSchema['title'].storage = atapi.AnnotationStorage()
HeaderSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(
    HeaderSchema,
    folderish=True,
    moveDiscussion=False
)

class Header(folder.ATFolder):
    """This header will display all contained images on top of your site"""
    implements(IHeader)
    meta_type = "Header"
    schema = HeaderSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')
    
    # -*- Your ATSchema to Python Property Bridges Here ... -*-

atapi.registerType(Header, PROJECTNAME)
