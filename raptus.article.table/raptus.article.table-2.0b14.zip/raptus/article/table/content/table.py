"""Definition of the Table content type
"""
from zope.interface import implements

try:
    from Products.LinguaPlone import public as atapi
except ImportError:
    # No multilingual support
    from Products.Archetypes import atapi
from Products.ATContentTypes.content import schemata
from Products.ATContentTypes.content import base

from raptus.article.table.field import TableColumnsField
from raptus.article.table.widget import TableColumnsWidget
from raptus.article.table.interfaces import ITable
from raptus.article.table.config import PROJECTNAME, OVERRIDE_DEFINITION
from raptus.article.core import RaptusArticleMessageFactory as _
from raptus.article.core.componentselection import ComponentSelectionWidget

TableSchema = schemata.ATContentTypeSchema.copy() + atapi.Schema((
        atapi.StringField('definition',
            languageIndependent=True,
            schemata = 'settings',
            vocabulary_factory = 'raptus.article.table.definitions',
            storage = atapi.AnnotationStorage(),
            widget = atapi.SelectionWidget(
                description = _(u'description_definition', default=u'Select from predefined table definitions'),
                label=_(u'label_definition', default=u'Table definition')
            ),
        ),
        atapi.StringField('style',
            vocabulary_factory = 'raptus.article.table.styles',
            languageIndependent=True,
            schemata = 'settings',
            write_permission = OVERRIDE_DEFINITION,
            storage = atapi.AnnotationStorage(),
            widget = atapi.SelectionWidget(
                description = _(u'description_style_override', default=u'Define the style of the table. This will override the style defined by the table definition if one is selected.'),
                label=_(u'label_style', default=u'Table style')
            ),
        ),
        TableColumnsField('columns',
            storage = atapi.AnnotationStorage(),
            schemata = 'settings',
            write_permission = OVERRIDE_DEFINITION,
            widget = TableColumnsWidget(
                description = _(u'description_columns_override', default=u'Define the columns of the table. This will override the columns defined by the table definition if one is selected.'),
                label= _(u'label_columns', default=u'Columns'),
            )
        ),
        atapi.LinesField('components',
            enforceVocabulary = True,
            vocabulary_factory = 'componentselectionvocabulary',
            storage = atapi.AnnotationStorage(),
            schemata = 'settings',
            widget = ComponentSelectionWidget(
                description = _(u'description_component_selection_table', default=u'Select the components in which this table should be displayed.'),
                label= _(u'label_component_selection', default=u'Component selection'),
            )
        ),
    ))

TableSchema['title'].storage = atapi.AnnotationStorage()
TableSchema['title'].required = False
TableSchema['description'].storage = atapi.AnnotationStorage()

for field in ('creators','allowDiscussion','contributors','location','language', 'nextPreviousEnabled', 'rights' ):
    if TableSchema.has_key(field):
        TableSchema[field].widget.visible = {'edit': 'invisible', 'view': 'invisible'}

schemata.finalizeATCTSchema(TableSchema, folderish=False, moveDiscussion=True)

class Table(base.ATCTOrderedFolder):
    """A table"""
    implements(ITable)
    
    portal_type = "Table"
    schema = TableSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')
    definition = atapi.ATFieldProperty('definition')
    style = atapi.ATFieldProperty('style')
    columns = atapi.ATFieldProperty('columns')

atapi.registerType(Table, PROJECTNAME)
