"""Definition of the VideoEmbed content type
"""
from zope.interface import implements

try:
    from Products.LinguaPlone import public as atapi
except ImportError:
    # No multilingual support
    from Products.Archetypes import atapi
from Products.ATContentTypes.content import schemata
from Products.ATContentTypes.content import link

from raptus.article.media.interfaces import IVideoEmbed
from raptus.article.media.config import PROJECTNAME
from raptus.article.core import RaptusArticleMessageFactory as _

VideoEmbedSchema = link.ATLinkSchema.copy()

VideoEmbedSchema['title'].required = False
VideoEmbedSchema['title'].storage = atapi.AnnotationStorage()
VideoEmbedSchema['description'].storage = atapi.AnnotationStorage()
VideoEmbedSchema['remoteUrl'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(VideoEmbedSchema, folderish=False, moveDiscussion=True)

class VideoEmbed(link.ATLink):
    """An embedded video"""
    implements(IVideoEmbed)
    
    portal_type = "VideoEmbed"
    schema = VideoEmbedSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')
    remoteUrl = atapi.ATFieldProperty('remoteUrl')

atapi.registerType(VideoEmbed, PROJECTNAME)
