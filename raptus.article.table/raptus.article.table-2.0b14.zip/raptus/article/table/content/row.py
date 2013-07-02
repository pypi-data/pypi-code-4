"""Definition of the Row content type
"""
from Acquisition import aq_parent, aq_inner
from zope.interface import implements
from zope.component import adapts

try:
    from Products.LinguaPlone import public as atapi
except ImportError:
    # No multilingual support
    from Products.Archetypes import atapi
from Products.ATContentTypes.content import schemata
from Products.ATContentTypes.content import base

from archetypes.schemaextender.interfaces import ISchemaExtender

from raptus.article.table.interfaces import IRow, IDefinition, ITable
from raptus.article.table.config import PROJECTNAME
from raptus.article.core import RaptusArticleMessageFactory as _

RowSchema = schemata.ATContentTypeSchema.copy()

RowSchema['title'].storage = atapi.AnnotationStorage()
RowSchema['title'].required = False
RowSchema['description'].storage = atapi.AnnotationStorage()

for field in ('creators','allowDiscussion','contributors','location','language', 'nextPreviousEnabled', 'rights' ):
    if RowSchema.has_key(field):
        RowSchema[field].widget.visible = {'edit': 'invisible', 'view': 'invisible'}

schemata.finalizeATCTSchema(RowSchema, folderish=False, moveDiscussion=True)

class Row(base.ATCTContent):
    """A row of a table"""
    implements(IRow)
    
    portal_type = "Row"
    schema = RowSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')
    
class Extender(object):
    adapts(Row)
    implements(ISchemaExtender)

    def __init__(self, context):
        self.context = context
     
    def getFields(self):
        context = aq_inner(self.context)
        if hasattr(context, 'object'):
            context = aq_inner(context.object)
        table = aq_parent(context)
        while not ITable.providedBy(table) and table is not None:
            table = aq_parent(table)
        if table is None:
            return []
        definition = IDefinition(table).getCurrentDefinition()
        fields = []
        for col in definition['columns']:
            fields.extend(col['utility'].fields(col['name'], col['title']))
        return fields

atapi.registerType(Row, PROJECTNAME)
