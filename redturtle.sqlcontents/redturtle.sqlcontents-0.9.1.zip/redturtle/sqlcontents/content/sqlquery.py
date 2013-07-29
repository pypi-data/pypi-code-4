"""Definition of the SQLQuery content type
"""
from Products.ATContentTypes.content import base, schemata
from Products.Archetypes import atapi
from Products.DataGridField import DataGridField, DataGridWidget, Column
from redturtle.sqlcontents import sqlcontentsMessageFactory as _
from redturtle.sqlcontents.config import PROJECTNAME
from redturtle.sqlcontents.interfaces.sqlquery import ISQLQuery
from zope.interface import implements


SQLQuerySchema = schemata.ATContentTypeSchema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-
    atapi.TextField(
        'query',
         storage=atapi.AnnotationStorage(),
         required=True,
         widget=atapi.TextAreaWidget(
         label=_(u"The query that should be executed"),
         description=_("help_query",
                       (u"For example "
                        u"SELECT * FROM TABLE LIMIT 10")),
            ),
    ),
    DataGridField(
        'column_names',
        storage=atapi.AnnotationStorage(),
        required=False,
        searchable=False,
        allow_delete=True,
        allow_insert=True,
        allow_reorder=True,
        columns=("key", "value"),
        widget=DataGridWidget(
                   label=_("Column names"),
                   description=_('help_column_names',
                                 (u"Assign human readable names to "
                                  u"the columns, they will be used for "
                                  u"presenting data in "
                                  u"a table inside the content view")),
                   visible={'view': 'hidden', 'edit': 'visible'},
                   columns={'key': Column(_('Column')),
                            'value': Column(_('Name'))},
        ),
    ),
    atapi.IntegerField('batch_size',
        widget=atapi.IntegerWidget(label=_("label_batch_size",
                                    "Rows per page"),
                            description=_("help_batch_size",
                                          u"The maximum number of rows "
                                          u"displayed in each page"),
                            ),
        default=20,
    ),
    atapi.TextField('introduction',
        searchable=False,
        default_output_type='text/x-html-safe',
        widget=atapi.RichWidget(
            label=_('label_introduction',
                    default=u'Introductive text'),
            description=_('help_introduction',
                          default=(u'This text will be displayed before the '
                                   u'query results')
                          ),
            rows=5,
            ),
    ),
    atapi.TextField('footer',
        searchable=False,
        default_output_type='text/x-html-safe',
        widget=atapi.RichWidget(
            label=_('label_footer', default=u'Footer text'),
            description=_('help_footer',
                          default=(u'This text will be displayed after the '
                                   u'query results')
                          ),
            rows=5,
            ),
    ),
))

# Set storage on fields copied from ATContentTypeSchema, making sure
# they work well with the python bridge properties.

SQLQuerySchema['title'].storage = atapi.AnnotationStorage()
SQLQuerySchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(SQLQuerySchema, moveDiscussion=False)


class SQLQuery(base.ATCTContent):
    """SQLQuery"""
    implements(ISQLQuery)

    meta_type = "SQLQuery"
    schema = SQLQuerySchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')

    # -*- Your ATSchema to Python Property Bridges Here ... -*-

atapi.registerType(SQLQuery, PROJECTNAME)
