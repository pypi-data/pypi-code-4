"""Definition of the Audio content type
"""
from zope.interface import implements

try:
    from Products.LinguaPlone import public as atapi
except ImportError:
    # No multilingual support
    from Products.Archetypes import atapi
from Products.ATContentTypes.content import schemata
from Products.ATContentTypes.content import file
from Products.validation import V_REQUIRED

from Products.ContentTypeValidator.validator import ContentTypeValidator

try:
    from plone.app.blob.field import BlobField as FileField
except ImportError:
    from Products.Archetypes.atapi import FileField

from raptus.article.media.interfaces import IAudio
from raptus.article.media.config import PROJECTNAME
from raptus.article.core import RaptusArticleMessageFactory as _

AudioSchema = file.ATFileSchema.copy() + atapi.Schema((
        FileField('file',
                required=True,
                primary=True,
                searchable=False,
                languageIndependent=False,
                storage = atapi.AnnotationStorage(migrate=True),
                validators = (('isNonEmptyFile', V_REQUIRED),
                              ('checkFileMaxSize', V_REQUIRED),
                              ContentTypeValidator(('audio/mpeg', 'audio/x-mp3', 'audio/x-mpeg', 'audio/mp3',))),
                widget = atapi.FileWidget(
                        description = '',
                        label=_(u'label_audio', default=u'Audio file'),
                        show_content_type = False,),
        ),
    ))

AudioSchema['title'].storage = atapi.AnnotationStorage()
AudioSchema['description'].storage = atapi.AnnotationStorage()

for field in ('creators','allowDiscussion','contributors','location','language', 'nextPreviousEnabled', 'rights' ):
    if AudioSchema.has_key(field):
        AudioSchema[field].widget.visible = {'edit': 'invisible', 'view': 'invisible'}

schemata.finalizeATCTSchema(AudioSchema, folderish=False, moveDiscussion=True)

class Audio(file.ATFile):
    """An audio file"""
    implements(IAudio)
    
    portal_type = "Audio"
    schema = AudioSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')

atapi.registerType(Audio, PROJECTNAME)
