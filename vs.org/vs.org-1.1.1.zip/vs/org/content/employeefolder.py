################################################################
# vs.org (C) 2011, Veit Schiele
################################################################

# $Id: employeefolder.py 2981 2011-03-16 10:54:12Z carsten $

"""
Definition of the Employeefolder content type
"""

from zope.interface import implements

from plone.app.portlets.portlets import base
from plone.memoize.instance import memoize

from AccessControl import ClassSecurityInfo
from compatible import atapi
from Products.ATContentTypes.content import folder
from Products.CMFCore.permissions import View
from Products.ATContentTypes.content import schemata
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from ..interfaces import IBase
from ..interfaces import IEmployeefolder
from ..config import PROJECTNAME

EmployeefolderSchema = folder.ATFolderSchema.copy() + atapi.Schema((

))

EmployeefolderSchema['title'].storage = atapi.AnnotationStorage()
EmployeefolderSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(
    EmployeefolderSchema,
    folderish=True,
    moveDiscussion=False
)


class Employeefolder(folder.ATFolder):
    """Employees of an institution or department"""
    implements(IEmployeefolder,IBase)

    meta_type = "Employeefolder"
    schema = EmployeefolderSchema
    security = ClassSecurityInfo()

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')

    security.declareProtected(View, 'getEmployeeFolder')
    def getEmployeeFolder(self):
        """ return the department """
        return self


class Renderer(base.Renderer):

    # render() will be called to render the portlet

    render = ViewPageTemplateFile('employeefolder.pt')

    # The 'available' property is used to determine if the portlet should
    # be shown.

    @property
    def available(self):
        return len(self._data()) > 0

    # To make the view template as simple as possible, we return dicts with
    # only the necessary information.

    def employeefolder(self):
        for brain in self._data():
            employee = brain.getObject()
            yield dict(title=registrant.name,
                       url=brain.getURL())

    @memoize
    def _data(self):
        context = aq_inner(self.context)
        limit = self.data.count

        query = dict(object_provides = IEmployee.__identifier__)

        query['sort_on'] = 'modified'
        query['sort_order'] = 'reverse'
        query['sort_limit'] = limit
        if not self.data.sitewide:
            query['path'] = '/'.join(context.getPhysicalPath())

        # Ensure that we only get active objects, even if the user would
        # normally have the rights to view inactive objects (as an
        # administrator would)
        query['effectiveRange'] = DateTime()

        catalog = getToolByName(context, 'portal_catalog')
        results = catalog(query)
        employeefolder = results[:limit]

        return employeefolder

atapi.registerType(Employeefolder, PROJECTNAME)
