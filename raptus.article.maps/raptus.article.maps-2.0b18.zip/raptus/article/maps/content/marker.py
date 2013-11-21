"""Definition of the Marker content type
"""
from zope.interface import implements

try:
    from Products.LinguaPlone import public as atapi
except ImportError:
    # No multilingual support
    from Products.Archetypes import atapi
from Products.ATContentTypes.content import schemata
from Products.ATContentTypes.content import base

from raptus.article.maps.interfaces import IMarker
from raptus.article.maps.config import PROJECTNAME
from raptus.article.core import RaptusArticleMessageFactory as _
from raptus.article.core.componentselection import ComponentSelectionWidget

MarkerSchema = schemata.ATContentTypeSchema.copy() + atapi.Schema((
        atapi.StringField('geocode',
            required=True,
            searchable=False,
            languageIndependent=True,
            storage = atapi.AnnotationStorage(),
            widget = atapi.StringWidget(
                description = '',
                label=_(u'label_street_zip_city', default=u'Street no., ZIP city')
            ),
        ),
        atapi.FloatField('latitude',
                required=True,
                searchable=False,
                languageIndependent=True,
                storage = atapi.AnnotationStorage(),
                widget = atapi.StringWidget(
                        description = '',
                        label=_(u'label_latitude', default=u'Latitude')
                ),
        ),
        atapi.FloatField('longitude',
                required=True,
                searchable=False,
                languageIndependent=True,
                storage = atapi.AnnotationStorage(),
                widget = atapi.StringWidget(
                        description = '',
                        label=_(u'label_longitude', default=u'Longitude')
                ),
        ),
        atapi.TextField('text',
                required=True,
                searchable=False,
                storage = atapi.AnnotationStorage(migrate=True),
                validators = ('isTidyHtmlWithCleanup',),
                #validators = ('isTidyHtml',),
                default_output_type = 'text/x-html-safe',
                widget = atapi.RichWidget(
                        description = '',
                        label = _(u'label_marker_text', default=u'Text'),
                        rows = 10),
        ),
    ))

MarkerSchema['title'].storage = atapi.AnnotationStorage()
MarkerSchema['title'].required = False
MarkerSchema['description'].storage = atapi.AnnotationStorage()

for field in ('creators','allowDiscussion','contributors','location','language', 'nextPreviousEnabled', 'rights' ):
    if MarkerSchema.has_key(field):
        MarkerSchema[field].widget.visible = {'edit': 'invisible', 'view': 'invisible'}

schemata.finalizeATCTSchema(MarkerSchema, folderish=False, moveDiscussion=True)

class Marker(base.ATCTContent):
    """A marker on a map"""
    implements(IMarker)
    
    portal_type = "Marker"
    schema = MarkerSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')
    latitude = atapi.ATFieldProperty('latitude')
    longitude = atapi.ATFieldProperty('longitude')
    depth = atapi.ATFieldProperty('text')

atapi.registerType(Marker, PROJECTNAME)
