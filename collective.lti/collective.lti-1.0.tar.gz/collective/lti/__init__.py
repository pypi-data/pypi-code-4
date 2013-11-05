from zope.i18nmessageid import MessageFactory
from Products.Archetypes.atapi import process_types
from Products.Archetypes.atapi import listTypes
from Products.CMFCore.utils import ContentInit
from Products.CMFCore import utils
from Products.CMFCore.permissions import AddPortalContent

from config import PROJECTNAME


def initialize(context):
    """Initializer called when used as a Zope 2 product."""

    import content

    content_types, constructors, ftis = process_types(
             listTypes(PROJECTNAME),
             PROJECTNAME)

    ContentInit(PROJECTNAME + ' Content',
                content_types=content_types,
                permission=AddPortalContent,
                extra_constructors=constructors,
                fti=ftis,
                ).initialize(context)	


ltiMessageFactory = MessageFactory('collective.lti')
