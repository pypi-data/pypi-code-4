from archetypes.schemaextender.field import ExtensionField
from archetypes.schemaextender.interfaces import IOrderableSchemaExtender
from archetypes.schemaextender.interfaces import IBrowserLayerAwareExtender
from Products.Archetypes import atapi
from Products.ATContentTypes.interfaces import IATContentType
from zope.interface import Interface
from five import grok
from collective.sliderfields.interfaces import IProductSpecific
from collective.sliderfields.interfaces import ISliderFieldsEnabled
from collective.sliderfields import MessageFactory as _

# Visit http://pypi.python.org/pypi/archetypes.schemaextender for full 
# documentation on writing extenders

class ExtensionImageField(ExtensionField, atapi.ImageField):
    pass

class ExtensionStringField(ExtensionField, atapi.StringField):
    pass

class SliderImage(grok.Adapter):

    # This applies to all AT Content Types, change this to
    # the specific content type interface you want to extend
    grok.context(ISliderFieldsEnabled)
    grok.name('collective.sliderfields.slider_image')
    grok.implements(IOrderableSchemaExtender, IBrowserLayerAwareExtender)
    grok.provides(IOrderableSchemaExtender)

    layer = IProductSpecific

    fields = [
        # add your extension fields here
        ExtensionImageField('slider_image',
            required=0,
            languageIndependent = 1,
            pil_quality = 100,
            storage = atapi.AttributeStorage(),
            schemata='settings',
            widget = atapi.ImageWidget(
                label = _(u'slider_image_label', default=u'Slider Image'),
                description = _(u'slider_image_description', default=u'Upload sliderimage.')
            )
        ),

        ExtensionStringField('slider_title',
            required=0,
            storage = atapi.AttributeStorage(),
            schemata='settings',
            widget = atapi.StringField._properties['widget'](
                label=_(u'slider_title_label', default=u'Slider Title'),
                description=_(u'slider_title_description',
                    default=(u'If set, the slider will use this title instead'
                        ' of the content title'))
            )
        ),

        ExtensionStringField('slider_description',
            required=0,
            storage = atapi.AttributeStorage(),
            schemata='settings',
            widget = atapi.StringField._properties['widget'](
                label=_(u'slider_description_label', default=u'Slider Description'),
                description=_(u'slider_description_description',
                    default=(u'If set, the slider will use this description instead'
                    ' of the content description')
                ),
            )
        )
    ]

    def __init__(self, context):
        self.context = context

    def getFields(self):
        return self.fields

    def getOrder(self, schematas):
        # you may reorder the fields in the schemata here
        return schematas
