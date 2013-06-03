################################################################
# vs.org (C) 2011, Veit Schiele
################################################################

# $Id$

from zope.component import adapter, getUtility, getMultiAdapter, queryMultiAdapter
from zope.container.interfaces import INameChooser
from plone.portlets.interfaces import IPortletAssignmentMapping, ILocalPortletAssignmentManager, IPortletManager

from plone.app.portlets.portlets import navigation

from Products.Archetypes.interfaces import IObjectInitializedEvent
from Products.CMFCore.utils import getToolByName

from ..interfaces import IInstitution, IDepartment
from ..portlets import institutionportlet
from ..portlets import departmentportlet
from ..portlets import equalinstitutionsportlet
from ..portlets import equaldepartmentsportlet

import logging
log = logging.getLogger('vs.org')

def setup_institution_portlets(obj, event):

    ptool = getToolByName(obj,'portal_url')
    c_uid = obj.UID()
    c_root =  '/' + '/'.join(ptool.getRelativeContentPath(obj))

    #left portlets
    manager = getUtility(IPortletManager, name=u'plone.leftcolumn')
    mapping = getMultiAdapter((obj, manager,), IPortletAssignmentMapping)

    has_navigation = False
    has_equal_institutions = False

    for value in mapping.values():
        if value.__name__ == 'navigation':
            has_navigation= True
        elif value.__name__ == 'label_equalinstitutionsportlet':
            has_equal_institutions = True

    if not has_navigation:
        assignment_navigation = navigation.Assignment(name=obj.Title(), root=c_root, currentFolderOnly=False, includeTop=False, topLevel=0, bottomLevel=2)

    if not has_equal_institutions:
        assignment_equalinstitutions = equalinstitutionsportlet.EqualInstitutionsPortletAssignment(institution_uid=c_uid)

    chooser = INameChooser(mapping)

    if not has_navigation:
        mapping[chooser.chooseName(None, assignment_navigation)] = assignment_navigation
    if not has_equal_institutions:
        mapping[chooser.chooseName(None, assignment_equalinstitutions)] = assignment_equalinstitutions

    # dont aquire portlets at left column
    assignable = queryMultiAdapter((obj, manager), ILocalPortletAssignmentManager)
    assignable.setBlacklistStatus('context', True)

    #right portlets 
    manager = getUtility(IPortletManager, name=u'plone.rightcolumn')
    mapping = getMultiAdapter((obj, manager,), IPortletAssignmentMapping)


    has_institution = False
    for value in mapping.values():
        if value.__name__ == 'label_institutionportlet':
            has_institution = True

    if not has_institution:
        assignment_institutionportlet = institutionportlet.InstitutionPortletAssignment(institution_uid=c_uid)
        chooser = INameChooser(mapping)
        mapping[chooser.chooseName(None, assignment_institutionportlet)] = assignment_institutionportlet

    # dont aquire portlets at right column
    assignable = queryMultiAdapter((obj, manager), ILocalPortletAssignmentManager)
    assignable.setBlacklistStatus('context', True)

#@adapter(IDepartment, IObjectInitializedEvent)
def setup_department_portlets(obj, event):

    # equaldepartments-portlet 
    manager = getUtility(IPortletManager, name=u'plone.leftcolumn')
    mapping = getMultiAdapter((obj, manager,), IPortletAssignmentMapping)

    has_equaldepartments = False
    for value in mapping.values():
        if value.__name__ == 'label_equaldepartmentsportlet':
            has_equaldepartments = True

    if not has_equaldepartments:
        assignment_equaldepartments = equaldepartmentsportlet.EqualDepartmentsPortletAssignment(department_uid=obj.UID())
        chooser = INameChooser(mapping)
        equaldepartments_name  = chooser.chooseName(None, assignment_equaldepartments)
        mapping[ equaldepartments_name] = assignment_equaldepartments

    # departmentportlet 
    manager = getUtility(IPortletManager, name=u'plone.rightcolumn')
    mapping = getMultiAdapter((obj, manager,), IPortletAssignmentMapping)

    has_department = False
    for value in mapping.values():
        if value.__name__ == 'label_departmentportlet':
            has_department = True
    if not has_department:
        assignment_department = departmentportlet.DepartmentPortletAssignment(department_uid=obj.UID())
        chooser = INameChooser(mapping)
        department_name  = chooser.chooseName(None, assignment_department)
        mapping[ department_name] = assignment_department

