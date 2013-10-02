#####################################################################
# zopyx.authoring
# (C) 2011, ZOPYX Limited, D-72070 Tuebingen. All rights reserved
#####################################################################

"""Definition of the AuthoringContentAggregator content type
"""

from zope.interface import implements

from AccessControl import ClassSecurityInfo
from Products.Archetypes import atapi
from Products.ATContentTypes.content import base
from Products.ATContentTypes.content import schemata
from Products.CMFCore.utils import getToolByName
# -*- Message Factory Imported Here -*-

from zopyx.authoring.interfaces import IAuthoringContentAggregator
from zopyx.authoring.config import PROJECTNAME
from zopyx.authoring import authoringMessageFactory as _
from archetypes.referencebrowserwidget.widget import ReferenceBrowserWidget

#from collective.referencedatagridfield import PKG_NAME
#from collective.referencedatagridfield import ReferenceDataGridField
#from collective.referencedatagridfield import ReferenceDataGridWidget

ALLOWED_TYPES = ('AuthoringContentFolder', 'Folder', 'Document', 'AuthoringContentPage')

AuthoringContentAggregatorSchema = schemata.ATContentTypeSchema.copy() + atapi.Schema((

    atapi.ReferenceField('refersTo1',
            schemata='default',
            relationship='refersTo1',
            allowed_types=ALLOWED_TYPES,
            allowed_types_method='getAllowedTypes',
            widget = ReferenceBrowserWidget(
                allow_search=True,
                allow_browse=True,
                show_indexes=False,
                force_close_on_insert=True,
                label=_(u'label_reference', u'Reference'), 
                visible = {'edit' : 'visible', 'view' : 'visible'}
            )
        ),

))

# Set storage on fields copied from ATContentTypeSchema, making sure
# they work well with the python bridge properties.

AuthoringContentAggregatorSchema['title'].storage = atapi.AnnotationStorage()
#AuthoringContentAggregatorSchema['title'].required = True
#AuthoringContentAggregatorSchema['title'].widget.visible = {'edit': 'hidden', 'view' : 'hidden'} 
AuthoringContentAggregatorSchema['description'].storage = atapi.AnnotationStorage()
AuthoringContentAggregatorSchema['description'].widget.visible = {'edit': 'hidden', 'view' : 'hidden'} 
AuthoringContentAggregatorSchema['description'].widget.visible = {'edit': 'hidden', 'view' : 'hidden'} 
schema = AuthoringContentAggregatorSchema
for field in schema.fields():
    if field.schemata in ('ownership', 'settings', 'categorization', 'dates'):
        field.widget.visible = {'edit': 'invisible', 'view' : 'invisible'} 

schemata.finalizeATCTSchema(AuthoringContentAggregatorSchema, moveDiscussion=False)


class AuthoringContentAggregator(base.ATCTContent):
    """AuthoringEnvironment content aggregator"""
    implements(IAuthoringContentAggregator)

    meta_type = "AuthoringContentAggregator"
    schema = AuthoringContentAggregatorSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')
    security = ClassSecurityInfo()

    # -*- Your ATSchema to Python Property Bridges Here ... -*-

    security.declarePublic('getIcon')
    def getIcon(self, relative_to_portal=0):
        """ getIcon() *does not work* """
        return 'aggregator.gif'

    def getAllowedTypes(self):
        return ALLOWED_TYPES

    def getReferencedContent(self):
        """ return the referenced content """

        result = list()
        ref_catalog = getToolByName(self, 'reference_catalog')
        for d in self.getRefersToContent():
            obj = ref_catalog.lookupObject(d['uid'])
            result.append(dict(title=obj.Title(),
                               description=obj.Description(),
                               icon_url=obj.getIcon(),
                               portal_type=obj.portal_type,
                               obj=obj,
                               url=obj.absolute_url(),
                               relative_url=obj.absolute_url(1),
                               ))
        return result

atapi.registerType(AuthoringContentAggregator, PROJECTNAME)
