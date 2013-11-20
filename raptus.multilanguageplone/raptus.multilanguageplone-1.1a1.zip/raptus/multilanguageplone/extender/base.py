from zope.interface import implements
from archetypes.schemaextender.interfaces import ISchemaExtender
from Products.Archetypes import PloneMessageFactory as _

from raptus.multilanguagefields import widgets
import fields

IMAGE_SIZES = {'large'   : (768, 768),
               'preview' : (400, 400),
               'mini'    : (200, 200),
               'thumb'   : (128, 128),
               'tile'    :  (64, 64),
               'icon'    :  (32, 32),
               'listing' :  (16, 16),
                }
try: # remove sizes if plone.app.imaging is available
    import plone.app.imaging
    IMAGE_SIZES = None
except ImportError:
    pass

class DefaultExtender(object):
    implements(ISchemaExtender)

    fields = [
        fields.StringField(
            name='title',
            required=1,
            searchable=1,
            default='',
            accessor='Title',
            widget=widgets.StringWidget(
                label = _(u'label_title', default=u'Title'),
                visible={'view' : 'invisible'},
                i18n_domain='plone',
            ),
            schemata='default',
        ),
        fields.LinesField(
            'subject',
            multiValued=1,
            accessor="Subject",
            searchable=True,
            isMetadata=True,
            widget=widgets.KeywordWidget(
                label=_(u'label_categories', default=u'Categories'),
                description=_(u'help_categories',
                              default=u'Also known as keywords, tags or labels, '
                                       'these help you categorize your content.'),
            ),
            schemata='categorization',
        ),
        fields.TextField(
            'description',
            default='',
            searchable=1,
            accessor="Description",
            default_content_type = 'text/plain',
            allowable_content_types = ('text/plain',),
            widget=widgets.TextAreaWidget(
                label=_(u'label_description', default=u'Description'),
                description=_(u'help_description',
                              default=u'A short summary of the content.'),
            ),
            schemata='default',
        ),
        fields.TextField(
            'rights',
            accessor="Rights",
            isMetadata=True,
            default_method='defaultRights',
            widget=widgets.TextAreaWidget(
                label=_(u'label_copyrights', default=u'Rights'),
                description=_(u'help_copyrights',
                              default=u'Copyright statement or other rights information on this item.'),
            ),
            schemata='ownership',
        ),
    ]

    def __init__(self, context):
         self.context = context

    def getFields(self):
        return self.fields
