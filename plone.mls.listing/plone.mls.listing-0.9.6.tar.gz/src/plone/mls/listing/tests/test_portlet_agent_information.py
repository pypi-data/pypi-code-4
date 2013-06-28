# -*- coding: utf-8 -*-
"""Test plone.mls.listing Agent Information portlet."""

# python imports
import unittest2 as unittest

# zope imports
from plone.app.portlets.storage import PortletAssignmentMapping
from plone.app.testing import TEST_USER_ID, setRoles
from plone.portlets import interfaces
from zope.component import getMultiAdapter, getUtility

# local imports
from plone.mls.listing.portlets import agent_information
from plone.mls.listing.testing import PLONE_MLS_LISTING_INTEGRATION_TESTING


class TestAgentInformationPortlet(unittest.TestCase):
    """Test Case for the Agent Information portlet."""

    layer = PLONE_MLS_LISTING_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ('Manager', ))
        self.portlet = getUtility(interfaces.IPortletType,
                                  name='portlets.AgentInformation')

    def test_portlet_type_registered(self):
        self.assertEqual(self.portlet.addview, 'portlets.AgentInformation')

    def test_interfaces(self):
        portlet = agent_information.Assignment()
        self.assertTrue(interfaces.IPortletAssignment.providedBy(portlet))
        self.assertTrue(
            interfaces.IPortletDataProvider.providedBy(portlet))

    def test_invoke_add_view(self):
        mapping = self.portal.restrictedTraverse(
            '++contextportlets++plone.leftcolumn')
        for item in mapping.keys():
            del mapping[item]
        addview = mapping.restrictedTraverse('+/' + self.portlet.addview)
        addview.createAndAdd(data={})
        self.assertEqual(len(mapping), 1)
        self.assertTrue(isinstance(mapping.values()[0],
                                   agent_information.Assignment))

    def test_invoke_edit_view(self):
        request = self.layer['request']
        mapping = PortletAssignmentMapping()
        mapping['foo'] = agent_information.Assignment()
        editview = getMultiAdapter((mapping['foo'], request), name='edit')
        self.assertIsInstance(editview, agent_information.EditForm)

    def test_renderer(self):
        request = self.layer['request']
        view = self.portal.restrictedTraverse('@@plone')
        manager = getUtility(interfaces.IPortletManager,
            name='plone.rightcolumn', context=self.portal)
        assignment = agent_information.Assignment()
        renderer = getMultiAdapter(
            (self.portal, request, view, manager, assignment),
            interfaces.IPortletRenderer)
        self.assertIsInstance(renderer, agent_information.Renderer)


class TestRenderer(unittest.TestCase):
    """Test Case for the Agent Information portlet renderer."""

    layer = PLONE_MLS_LISTING_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ('Manager', ))

    def renderer(self, context=None, request=None, view=None, manager=None,
                 assignment=None):
        context = context or self.portal
        request = request or self.layer['request']
        view = view or self.portal.restrictedTraverse('@@plone')
        manager = manager or getUtility(interfaces.IPortletManager,
                                        name='plone.rightcolumn',
                                        context=self.portal)
        assignment = assignment or agent_information.Assignment()

        return getMultiAdapter((context, request, view, manager, assignment),
                               interfaces.IPortletRenderer)

    def test_title(self):
        r = self.renderer(
            context=self.portal, assignment=agent_information.Assignment())
        self.assertEqual('Agent Information', r.title)

    def test_custom_title(self):
        r = self.renderer(
            context=self.portal, assignment=agent_information.Assignment(
                heading=u'My Title'))
        self.assertEqual('My Title', r.title)
