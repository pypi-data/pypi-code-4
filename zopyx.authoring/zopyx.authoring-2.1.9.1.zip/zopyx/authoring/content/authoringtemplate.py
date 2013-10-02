"""Definition of the AuthoringTemplate content type
"""

from zope.interface import implements, directlyProvides

from Products.Archetypes import atapi
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content import schemata

from zopyx.authoring import authoringMessageFactory as _
from zopyx.authoring.interfaces import IAuthoringTemplate
from zopyx.authoring.config import PROJECTNAME
from Products.CMFCore.ContentTypeRegistry import manage_addRegistry

from zopyx.smartprintng.plone.resources import resources_registry

AuthoringTemplateSchema = folder.ATFolderSchema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-

    atapi.StringField('resourceOnFilesystem',
                      vocabulary='getResourcesOnFilesystem',
                      widget=atapi.SelectionWidget(label=_('label_resource_on_filesystem', default='Resources on filesystem'),
                                                   format='select',
                                                   ),
                      ),

))

# Set storage on fields copied from ATFolderSchema, making sure
# they work well with the python bridge properties.

AuthoringTemplateSchema['title'].storage = atapi.AnnotationStorage()
AuthoringTemplateSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(
    AuthoringTemplateSchema,
    folderish=True,
    moveDiscussion=False
)

class predicate(object):
    """ Used for content type registry """

    def __init__(self, id, extensions):
        self.extensions = extensions
        self.id = id

class AuthoringTemplate(folder.ATFolder):
    """Authoring Template"""
    implements(IAuthoringTemplate)

    meta_type = "AuthoringTemplate"
    schema = AuthoringTemplateSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')
    
    # -*- Your ATSchema to Python Property Bridges Here ... -*-

    def at_post_create_script(self, ):

        # content-type registry
        manage_addRegistry(self)
        registry = self['content_type_registry']
        registry.addPredicate('images', 'extension')
        registry.addPredicate('templates', 'extension')
        registry.addPredicate('stylesheet', 'extension')
        registry.addPredicate('files', 'extension')
        registry.doUpdatePredicate('images', predicate('images', 'jpg jpeg png gif JPG JPEG PNG GIF'), 'AuthoringImageResource', self.REQUEST)
        registry.doUpdatePredicate('stylesheet', predicate('stylesheet', 'css CSS styles STYLES'), 'AuthoringStylesheet', self.REQUEST)
        registry.doUpdatePredicate('templates', predicate('templates', 'pt PT template TEMPLATE'), 'AuthoringMasterTemplate', self.REQUEST)
        registry.doUpdatePredicate('files', predicate('files', 'ttf TTF otf OTF dic DIC'), 'AuthoringBinaryResource', self.REQUEST)

    def getResourcesOnFilesystem(self):
        result = atapi.DisplayList()
        result.add('', _(u'label_no_edit_resource_ttw', u'No, I edit my resources through the web'))
        for r in resources_registry.keys():
            result.add(r, _(u'Use resource') + ':' + r)
        return result

atapi.registerType(AuthoringTemplate, PROJECTNAME)
