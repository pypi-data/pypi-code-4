################################################################
# vs.org (C) 2011, Veit Schiele
################################################################

# $Id: employee.py 2981 2011-03-16 10:54:12Z carsten $

"""
Definition of the Employee content type
"""

from AccessControl import ClassSecurityInfo
from zope.interface import implements

from compatible import atapi
from Products.ATContentTypes.content import base
from Products.ATContentTypes.content import schemata
from Products.DataGridField.Column import Column
from Products.DataGridField.SelectColumn import SelectColumn
from Products.DataGridField.CheckboxColumn import CheckboxColumn
from Products.DataGridField import DataGridField, DataGridWidget, FixedRow

from .. import orgMessageFactory as _
from ..interfaces import IBase
from ..interfaces import IEmployee
from ..config import PROJECTNAME
from base import BaseSchema
from numbers import NumbersMixin

EmployeeSchema = schemata.ATContentTypeSchema.copy() + BaseSchema.copy() + atapi.Schema((

    atapi.StringField(
        'salutation',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_(u"label_salutation"),
            description=_(u"help_salutation"),
        ),
    ),

    atapi.StringField(
        'degree',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_(u"label_degree"),
            description=_(u"help_degree"),
        ),
    ),

    atapi.StringField(
        'degreeAfter',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_(u"label_degree_after"),
            description=_(u"help_degree_after"),
        ),
    ),


    atapi.StringField(
        'firstname',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_(u"label_firstname"),
            description=_(u"help_firstname"),
        ),
    ),

    atapi.StringField(
        'middlename',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_(u"label_middlename"),
            description=_(u"help_middlename"),
        ),
    ),

    atapi.StringField(
        'lastname',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_(u"label_lastname"),
            description=_(u"help_lastname"),
        ),
    ),

    atapi.StringField(
        'position',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_(u"label_position"),
            description=_(u"help_position"),
        ),
    ),

    atapi.ComputedField(
        'title',
        storage=atapi.AnnotationStorage(),
        widget=atapi.ComputedWidget(
            label=_(u"label_title"),
            description=_(u"help_title"),
        ),
        expression='context.DisplayName()',
        mode='r',
        accessor="Title"
    ),

    atapi.LinesField(
        'notes',
        storage=atapi.AnnotationStorage(),
        widget=atapi.LinesWidget(
            label=_(u"label_notes"),
            description=_(u"help_notes"),
        ),
    ),

))

EmployeeSchema['title'].storage = atapi.AnnotationStorage()
EmployeeSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(EmployeeSchema, moveDiscussion=False)


class Employee(base.ATCTContent, NumbersMixin):
    """Employee of an institution and/or departments"""
    security = ClassSecurityInfo()
    implements(IEmployee, IBase)
    meta_type = 'Employee'
    numbers_vocabulary = 'number_types_employee'
    schema = EmployeeSchema


    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')
    salutation = atapi.ATFieldProperty('salutation')
    degree = atapi.ATFieldProperty('degree')
    firstname = atapi.ATFieldProperty('firstname')
    middlename = atapi.ATFieldProperty('middlename')
    lastname = atapi.ATFieldProperty('lastname')
    position = atapi.ATFieldProperty('position')
    notes = atapi.ATFieldProperty('notes')

    def at_post_edit_script(self, *args, **kw):
        """ Filter out empty number fields """
        super(Employee, self).at_post_edit_script(*args, **kw)
        numbers = self.getNumbers()
        numbers = [d for d in numbers if d['number']]
        self.setNumbers(numbers)

    security.declarePublic('DisplayName')
    def DisplayName(self, showPosition=True):
        """Returns the complete Name"""
        lst = [self.getSalutation(), 
               self.getDegree(), 
               self.getFirstname(), 
               self.getMiddlename(), 
               self.getLastname()]
        displayname = ' '.join([(x or '').strip() for x in lst])
        position = self.getPosition()
        degreeAfter = self.getDegreeAfter()
        if degreeAfter:
            displayname += ", " + degreeAfter
        if showPosition and position:
            displayname += ", " + position
        return displayname

    security.declarePublic('DisplayNamePosition')
    def DisplayNamePosition(self):
        """Returns the complete Name (without salutation) and position"""
        lst = [self.getDegree(),
               self.getFirstname(),
               self.getMiddlename(), 
               self.getLastname()]
        displayname = ' '.join([(x or '').strip() for x in lst])
        position = self.getPosition()
        if position:
            displayname += ", " + position
        return displayname

    def setTitle(self, title):
        """ ISE-11: Dummy mutator for 'title'. Since 'title' is a computed
            field we must provide a dummy implementation in order to let the
            setTitle() operation work on the object itself instead of letting Plone
            call the setTitle() on the acquisition parent (causing a EmployeeFolder
            renaming operation).
        """
        pass

atapi.registerType(Employee, PROJECTNAME)
