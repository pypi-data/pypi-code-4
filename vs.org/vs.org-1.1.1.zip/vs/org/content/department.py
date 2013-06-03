################################################################
# vs.org (C) 2011, Veit Schiele
################################################################

# $Id: department.py 2983 2011-03-16 11:36:36Z carsten $

"""
Definition of the Department content type
"""

from AccessControl import ClassSecurityInfo

from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletAssignmentMapping
from zope.container.interfaces import INameChooser
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.interface import implements

from archetypes.referencebrowserwidget.widget import ReferenceBrowserWidget
from compatible import atapi
from Products.Archetypes.interfaces import IObjectInitializedEvent
from Products.ATContentTypes.configuration import zconf
from Products.ATContentTypes.content import base
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content import schemata
from Products.ATContentTypes.lib.constraintypes import ConstrainTypesMixinSchema
from Products.CMFCore.permissions import View

# -*- Message Factory Imported Here -*-
from .. import orgMessageFactory as _

from ..interfaces import IBase
from ..interfaces import IDepartment
from ..config import PROJECTNAME
from ..config import DEPARTMENTS_PORTLET_COLUMN
from ..portlets import departmentportlet
from base import BaseSchema
from numbers import NumbersMixin

DepartmentSchema = folder.ATFolderSchema.copy() + ConstrainTypesMixinSchema.copy() + BaseSchema.copy() + atapi.Schema((

    atapi.TextField('text',
              required=False,
              searchable=True,
              primary=True,
              storage = atapi.AnnotationStorage(),
              validators = ('isTidyHtmlWithCleanup',),
              default_output_type = 'text/x-html-safe',
              widget = atapi.RichWidget(
                        description='',
                        label=_(u'label_body_text', default=u'Body Text'),
                        rows=25,
                        allow_file_upload=zconf.ATDocument.allow_document_upload),
    ),

    atapi.ReferenceField(
        name='employees',
        keepReferencesOnCopy=1,
        multiValued=1,
        allowed_types=('Employee',),
        relationship='isEmployee',
        widget=ReferenceBrowserWidget(
            show_review_state=1,
            allow_sorting=1,
            label=_(u'label_employees',),
        ),
    ),

    atapi.TextField(
        'buildingsection',
        required=True,
        searchable=True,
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_(u"label_building_section"),
            description=_(u"help_building_section"),
        ),
    ),


    atapi.LinesField(
        'specialisation',
        accessor='Specialisation',
        required=False,
        searchable=True,
        storage=atapi.AnnotationStorage(),
        widget=atapi.KeywordWidget(
            label=_(u"label_specialisation"),
            description=_(u"help_specialisation"),
        ),
    ),

))

DepartmentSchema['title'].storage = atapi.AnnotationStorage()
DepartmentSchema['description'].storage = atapi.AnnotationStorage()
DepartmentSchema['text'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(
    DepartmentSchema,
    folderish=True,
    moveDiscussion=False
)


class Department(folder.ATFolder, NumbersMixin):
    """Department of an institution"""

    implements(IDepartment, IBase)
    meta_type = 'Department'
    numbers_vocabulary = 'number_types_department'
    security = ClassSecurityInfo()
    schema = DepartmentSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')

    buildingsection = atapi.ATFieldProperty('buildingsection')
    specialisation = atapi.ATFieldProperty('specialisation')

    security.declareProtected(View, 'getDepartment')
    def getDepartment(self):
        """ return the department """
        return self

    def at_post_edit_script(self, *args, **kw):
        """ Filter out empty number fields """
        super(Department, self).at_post_edit_script(*args, **kw)
        numbers = self.getNumbers()
        numbers = [d for d in numbers if d['number']]
        self.setNumbers(numbers)

atapi.registerType(Department, PROJECTNAME)

@adapter(IDepartment, IObjectInitializedEvent)
def setup_department_portlets(obj, event):
    column = getUtility(IPortletManager, name=DEPARTMENTS_PORTLET_COLUMN)
    manager = getMultiAdapter((obj, column,), IPortletAssignmentMapping)
    
    has_department = False
    for value in manager.values():
        if value.__name__ == 'label_departmentportlet':
            has_department = True
    if not has_department:
        assignment_department = departmentportlet.DepartmentPortletAssignment(department_uid=obj.UID())
    
        chooser = INameChooser(manager)
        department_name  = chooser.chooseName(None, assignment_department) 
        manager[chooser.chooseName(None, assignment_department)] = assignment_department

