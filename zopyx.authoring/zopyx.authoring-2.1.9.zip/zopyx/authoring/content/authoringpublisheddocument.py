"""Definition of the AuthoringPublishedDocument content type
"""

from zope.interface import implements
from zope.component import adapter, getUtility, getMultiAdapter, queryMultiAdapter
try:
    from zope.app.container.interfaces import INameChooser
except ImportError:
    from zope.container.interfaces import INameChooser

from plone.portlets.interfaces import IPortletAssignmentMapping, ILocalPortletAssignmentManager, IPortletManager

from Products.Archetypes import atapi
from Products.ATContentTypes.content import base
from Products.ATContentTypes.content import schemata
from Products.ATContentTypes.content.document import ATDocument, ATDocumentSchema
from Products.CMFCore.utils import getToolByName

# -*- Message Factory Imported Here -*-

from zopyx.authoring.interfaces import IAuthoringPublishedDocument
from zopyx.authoring.config import PROJECTNAME

from ..portlets import publishedcontentportlet

COUNTER_VOCAB = atapi.DisplayList((
    ('h1', 'H1'),
    ('h2', 'H2'),
))

AuthoringPublishedDocumentSchema = ATDocumentSchema.copy() +  atapi.Schema((
    # chapter specific styles
    atapi.TextField('styles', widget=atapi.TextAreaWidget()),
    # styles extract from the DOC conversion
    atapi.TextField('officeStyles', widget=atapi.TextAreaWidget()),
    atapi.StringField('countersStartWith', 
                      default='h1',
                      vocabulary=COUNTER_VOCAB,
                      widget=atapi.SelectionWidget(label=u'Counter starts with...')
                      ),
))

# Set storage on fields copied from ATContentTypeSchema, making sure
# they work well with the python bridge properties.

AuthoringPublishedDocumentSchema['title'].storage = atapi.AnnotationStorage()
AuthoringPublishedDocumentSchema['description'].storage = atapi.AnnotationStorage()
schemata.finalizeATCTSchema(AuthoringPublishedDocumentSchema, moveDiscussion=False)


class AuthoringPublishedDocument(ATDocument):
    """Authoring Project Published Document"""
    implements(IAuthoringPublishedDocument)

    meta_type = "AuthoringPublishedDocument"
    schema = AuthoringPublishedDocumentSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')

    # -*- Your ATSchema to Python Property Bridges Here ... -*-

    def manage_afterAdd(self, obj, container):
        """ Setup portlet """

        manager = getUtility(IPortletManager, name=u'plone.leftcolumn')
        mapping = getMultiAdapter((obj, manager,), IPortletAssignmentMapping)

        # don't add a portlet twice
        for value in mapping.values():
            if value.__name__ == 'publishedcontentportlet':
                return 

        chooser = INameChooser(mapping)
        assignable = queryMultiAdapter((obj, manager), ILocalPortletAssignmentManager)
        assignable.setBlacklistStatus('context', True)
        assignment = publishedcontentportlet.Assignment()
        chooser = INameChooser(mapping)
        mapping._data.clear()
        mapping[chooser.chooseName(None, assignment)] = assignment

atapi.registerType(AuthoringPublishedDocument, PROJECTNAME)
