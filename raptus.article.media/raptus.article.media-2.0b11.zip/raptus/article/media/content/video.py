"""Definition of the Video content type
"""
from AccessControl import ClassSecurityInfo
from zope.interface import implements

try:
    from Products.LinguaPlone import public as atapi
except ImportError:
    # No multilingual support
    from Products.Archetypes import atapi
from Products.CMFCore.permissions import View
from Products.ATContentTypes.content import schemata
from Products.ATContentTypes.content import file
from Products.ATContentTypes.content.base import ATCTFileContent
from Products.ATContentTypes.configuration import zconf
from Products.validation import V_REQUIRED

from Products.ContentTypeValidator.validator import ContentTypeValidator

try:
    from plone.app.blob.field import BlobField as FileField, ImageField
except ImportError:
    from Products.Archetypes.atapi import FileField, ImageField

from raptus.article.media.interfaces import IVideo
from raptus.article.media.config import PROJECTNAME
from raptus.article.core import RaptusArticleMessageFactory as _

valid_types = ['video/x-flv', 'application/x-flash-video', 'flv-application/octet-stream', 'video/flv', 'video/mp4', 'video/mp4v-es', 'video/x-m4v']
try:
    from stxnext.transform.avi2flv import avi_to_flv
    convert_types = ('video/x-avi', 'video/x-msvideo', 'video/x-ms-wmv', 'video/quicktime',)
    def register_patch():
        return avi_to_flv.Avi2Flv(inputs=convert_types)
    avi_to_flv.register = register_patch
    valid_types.extend(convert_types)
except:
    pass

VideoSchema = file.ATFileSchema.copy() + atapi.Schema((
        FileField('file',
                required=True,
                primary=True,
                searchable=False,
                languageIndependent=False,
                storage = atapi.AnnotationStorage(migrate=True),
                validators = (('isNonEmptyFile', V_REQUIRED),
                              ('checkFileMaxSize', V_REQUIRED),
                              ContentTypeValidator(valid_types)),
                widget = atapi.FileWidget(
                        description = '',
                        label=_(u'label_video', default=u'Video file'),
                        show_content_type = False,),
        ),
        ImageField('image',
                required=False,
                languageIndependent=False,
                storage = atapi.AnnotationStorage(migrate=True),
                swallowResizeExceptions = zconf.swallowImageResizeExceptions.enable,
                pil_quality = zconf.pil_config.quality,
                pil_resize_algo = zconf.pil_config.resize_algo,
                max_size = zconf.ATImage.max_image_dimension,
                sizes= {'large'   : (768, 768),
                        'preview' : (400, 400),
                        'mini'    : (200, 200),
                        'thumb'   : (128, 128),
                        'tile'    :  (64, 64),
                        'icon'    :  (32, 32),
                        'listing' :  (16, 16),
                       },
                validators = (('isNonEmptyFile', V_REQUIRED),
                              ('checkImageMaxSize', V_REQUIRED)),
                widget = atapi.ImageWidget(
                        description = '',
                        label= _(u'label_image', default=u'Image'),
                        show_content_type = False,)
        ),
    ))

VideoSchema['title'].storage = atapi.AnnotationStorage()
VideoSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(VideoSchema, folderish=False, moveDiscussion=True)

class Video(file.ATFile):
    """A video file"""
    implements(IVideo)
    
    portal_type = "Video"
    schema = VideoSchema

    security = ClassSecurityInfo()

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')

    security.declareProtected(View, 'tag')
    def tag(self, **kwargs):
        """Generate image tag using the api of the ImageField
        """
        return self.getField('image').tag(self, **kwargs)

    def __bobo_traverse__(self, REQUEST, name):
        """Transparent access to image scales
        """
        if name.startswith('image'):
            field = self.getField('image')
            image = None
            if name == 'image':
                image = field.getScale(self)
            else:
                scalename = name[len('image_'):]
                if scalename in field.getAvailableSizes(self):
                    image = field.getScale(self, scale=scalename)
            if image is not None and not isinstance(image, basestring):
                # image might be None or '' for empty images
                return image

        return ATCTFileContent.__bobo_traverse__(self, REQUEST, name)

atapi.registerType(Video, PROJECTNAME)
