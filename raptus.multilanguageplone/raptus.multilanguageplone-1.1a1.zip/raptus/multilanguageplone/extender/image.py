from zope.component import adapts
from Products.Archetypes import PloneMessageFactory as _

from Products.Archetypes.atapi import AnnotationStorage
from Products.ATContentTypes.configuration import zconf
from Products.validation import V_REQUIRED
from Products.ATContentTypes.content.image import ATImage

from raptus.multilanguagefields import widgets
import fields

from base import DefaultExtender, IMAGE_SIZES

title_field = [
        fields.StringField(
            name='title',
            required=False,
            searchable=True,
            default='',
            accessor='Title',
            widget=widgets.StringWidget(
                label_msgid='label_title',
                visible={'view' : 'invisible'},
                i18n_domain='plone',
            ),
        ),]

class ImageExtender(DefaultExtender):
    adapts(ATImage)

    fields = DefaultExtender.fields + title_field + [
        fields.ImageField('image',
            required=True,
# we got an error with this attribute on Plone 3.3
# Tried to add 'text___fr___' as primary field but <Products.Archetypes.Schema.Schema object at 0x0AE1BBD0> already has the primary field 'text'
#
# we need the primary marker here to have multilanguage images working
            primary=True,
            languageIndependent=False,
            storage = AnnotationStorage(migrate=True),
            swallowResizeExceptions = zconf.swallowImageResizeExceptions.enable,
            pil_quality = zconf.pil_config.quality,
            pil_resize_algo = zconf.pil_config.resize_algo,
            max_size = zconf.ATImage.max_image_dimension,
            sizes=IMAGE_SIZES,
            widget = widgets.ImageWidget(
                description = '',
                label= _(u'label_image', default=u'Image'),
                show_content_type = False,
            )
        ),
    ]

try:
    from zope.interface import implements
    from plone.app.blob.interfaces import IATBlobImage
    from archetypes.schemaextender.interfaces import ISchemaModifier
    from plone.app.imaging.interfaces import IImageScaleHandler
    
    class BlobImageExtender(DefaultExtender):
        adapts(IATBlobImage)

        fields = DefaultExtender.fields + title_field
        
    class BlobImageModifier(object):
        adapts(IATBlobImage)
        implements(ISchemaModifier)
        
        field = fields.BlobImageField('image',
                    required = True,
                    primary = True,
                    accessor = 'getImage',
                    mutator = 'setImage',
                    languageIndependent = True,
                    storage = AnnotationStorage(migrate=True),
                    swallowResizeExceptions = zconf.swallowImageResizeExceptions.enable,
                    pil_quality = zconf.pil_config.quality,
                    pil_resize_algo = zconf.pil_config.resize_algo,
                    max_size = zconf.ATImage.max_image_dimension,
                    validators = (('isNonEmptyFile', V_REQUIRED),
                                  ('checkImageMaxSize', V_REQUIRED)),
                    widget = widgets.ImageWidget(
                        description = '',
                        label=_(u'label_image', default=u'Image'),
                        show_content_type = False,
                    )
                )
        
        def __init__(self, context):
            self.context = context
            
        def fiddle(self, schema):
            schema['image'] = self.field
            return schema
except ImportError:
    pass
