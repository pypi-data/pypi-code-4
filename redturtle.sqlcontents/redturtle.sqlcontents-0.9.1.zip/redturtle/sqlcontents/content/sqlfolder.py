# -*- coding: utf-8 -*-
"""Definition of the SQLFolder content type
"""
from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.content import folder, schemata
from Products.Archetypes import atapi
from redturtle.sqlcontents import sqlcontentsMessageFactory as _
from redturtle.sqlcontents.config import PROJECTNAME
from redturtle.sqlcontents.interfaces.sqlfolder import ISQLFolder
from zope.interface import implements

SQLFolderSchema = folder.ATFolderSchema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-
    atapi.StringField(
        'connection_url',
        storage=atapi.AnnotationStorage(),
        required=True,
        mode='w',
        widget=atapi.StringWidget(
            label=_(u"Connection string"),
            description=_("help_connection_url",
                          u"Connection URL compliant with the RFC-1738 "
                          u"standard, for example "
                          u"postgresql://user:passwd@127.0.0.1:5432/testdb"),
            ),
    )
))

# Set storage on fields copied from ATFolderSchema, making sure
# they work well with the python bridge properties.

SQLFolderSchema['title'].storage = atapi.AnnotationStorage()
SQLFolderSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(
    SQLFolderSchema,
    folderish=True,
    moveDiscussion=False
)


class SQLFolder(folder.ATFolder):
    """SQLFolder"""
    implements(ISQLFolder)

    meta_type = "SQLFolder"
    schema = SQLFolderSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')

    # -*- Your ATSchema to Python Property Bridges Here ... -*-

    security = ClassSecurityInfo()


atapi.registerType(SQLFolder, PROJECTNAME)
