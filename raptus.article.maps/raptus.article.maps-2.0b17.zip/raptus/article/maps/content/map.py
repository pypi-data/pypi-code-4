"""Definition of the Map content type
"""
from zope.interface import implements
from Products.Archetypes.utils import IntDisplayList

try:
    from Products.LinguaPlone import public as atapi
except ImportError:
    # No multilingual support
    from Products.Archetypes import atapi
from Products.ATContentTypes.content import schemata
from Products.ATContentTypes.content import base

from raptus.article.maps.interfaces import IMap
from raptus.article.maps.config import PROJECTNAME
from raptus.article.core import RaptusArticleMessageFactory as _
from raptus.article.core.componentselection import ComponentSelectionWidget


MapSchema = schemata.ATContentTypeSchema.copy() + atapi.Schema((
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
        atapi.IntegerField('depth',
            required=False,
            searchable=False,
            languageIndependent=True,
            enforceVocabulary=True,
            vocabulary=IntDisplayList([(i, str(i),) for i in range(0, 20)]),
            default=10,
            storage = atapi.AnnotationStorage(),
            widget = atapi.SelectionWidget(
                description = '',
                label=_(u'label_depth', default=u'Depth')
            ),
        ),
        atapi.BooleanField('hideControls',
            required=False,
            searchable=False,
            languageIndependent=True,
            storage = atapi.AnnotationStorage(),
            widget = atapi.BooleanWidget(
                description = '',
                label=_(u'label_hide_controls', default=u'Hide controls')
            ),
        ),
        atapi.BooleanField('enableScrollZoom',
            required=False,
            searchable=False,
            languageIndependent=True,
            default=False,
            storage = atapi.AnnotationStorage(),
            widget = atapi.BooleanWidget(
                description = '',
                label=_(u'label_enable_scroll', default=u'Enable scroll wheel zoom')
            ),
        ),
        atapi.BooleanField('enableStreetView',
            required=False,
            searchable=False,
            languageIndependent=True,
            default=False,
            storage = atapi.AnnotationStorage(),
            widget = atapi.BooleanWidget(
                description = '',
                label=_(u'label_enable_streetview', default=u'Enable street view')
            ),
        ),
        atapi.BooleanField('enableCenteredView',
            required=False,
            searchable=False,
            languageIndependent=True,
            default=True,
            storage = atapi.AnnotationStorage(),
            widget = atapi.BooleanWidget(
                description = '',
                label=_(u'label_enable_centeredview', default=u'Enable centered view')
            ),
        ),
        atapi.StringField('mapType',
            required=True,
            searchable=False,
            languageIndependent=True,
            default='G_NORMAL_MAP',
            enforceVocabulary=True,
            storage = atapi.AnnotationStorage(),
            vocabulary=(('ROADMAP', _(u'Roadmap')),
                        ('SATELLITE', _(u'Satellite')),
                        ('HYBRID', _(u'Hybrid')),
                        ('TERRAIN', _(u'Terrain')),),
            widget = atapi.SelectionWidget(
                format = 'radio',
                description = '',
                label=_(u'label_map_type', default=u'Map type')
            ),
        ),
        atapi.StringField('layer',
            required=False,
            searchable=False,
            languageIndependent=True,
            storage = atapi.AnnotationStorage(),
            widget = atapi.StringWidget(
                description = '',
                label=_(u'label_layer', default=u'Layer'),
                visible=False, # not supported from gomap jquery plugin
            ),
        ),
        atapi.LinesField('components',
            enforceVocabulary = True,
            vocabulary_factory = 'componentselectionvocabulary',
            storage = atapi.AnnotationStorage(),
            schemata = 'settings',
            widget = ComponentSelectionWidget(
                description = _(u'description_component_selection_map', default=u'Select the components in which this map should be displayed.'),
                label= _(u'label_component_selection', default=u'Component selection'),
            )
        ),
    ))

MapSchema['title'].storage = atapi.AnnotationStorage()
MapSchema['title'].required = False
MapSchema['description'].storage = atapi.AnnotationStorage()

for field in ('creators','allowDiscussion','contributors','location','language', 'nextPreviousEnabled', 'rights' ):
    if MapSchema.has_key(field):
        MapSchema[field].widget.visible = {'edit': 'invisible', 'view': 'invisible'}

schemata.finalizeATCTSchema(MapSchema, folderish=False, moveDiscussion=True)

class Map(base.ATCTFolder):
    """A map"""
    implements(IMap)

    portal_type = "Map"
    schema = MapSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')
    latitude = atapi.ATFieldProperty('latitude')
    longitude = atapi.ATFieldProperty('longitude')
    geocode = atapi.ATFieldProperty('geocode')
    depth = atapi.ATFieldProperty('depth')
    hideControls = atapi.ATFieldProperty('hideControls')
    enableScrollZoom = atapi.ATFieldProperty('enableScrollZoom')
    center = atapi.ATFieldProperty('enableCenteredView')
    mapType = atapi.ATFieldProperty('mapType')
    layer = atapi.ATFieldProperty('layer')

    def getMapType(self):
        """ backward compatibility
            merge old maptype to map v3
        """
        value = self.Schema()['mapType'].get(self)
        if value.startswith('G_'):
            if value == 'G_NORMAL_MAP':
                return 'ROADMAP'
            return value[2:-4]
        return value


atapi.registerType(Map, PROJECTNAME)
