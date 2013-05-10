# -*- coding: utf-8 -*-
from base import BaseTestCase
from collective.contentrules.subscription.testing import CONTENTRULESSUBSCRIPTION_FUNCTIONAL_TESTING
from Products.CMFCore.utils import getToolByName
from plone.app.contentrules.rule import Rule
from collective.contentrules.subscription import SUBSCRIPTION_TOOL
from zope.app.container.interfaces import IObjectAddedEvent, INameChooser
from plone.contentrules.engine.interfaces import IRuleStorage
from zope.component import getUtility
from collective.contentrules.subscription.actions.mail import MailSubscriptionsAction


class TestTool(BaseTestCase):

    layer = CONTENTRULESSUBSCRIPTION_FUNCTIONAL_TESTING

    def setUp(self):
        """
        """
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.markRequestWithLayer()

    def test_tool_present(self):
        """
        test if the tool is correctly created
        """
        tool = getToolByName(self.portal, SUBSCRIPTION_TOOL, None)
        self.assertNotEquals(None, tool)


class TestToolFunctionalities(BaseTestCase):

    layer = CONTENTRULESSUBSCRIPTION_FUNCTIONAL_TESTING

    def setUp(self):
        """
        """
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.markRequestWithLayer()

    def test_empty_tool(self):
        """
        The tool is empty, try to get some results
        """
        tool = getToolByName(self.portal, SUBSCRIPTION_TOOL, None)
        self.assertEquals(tool.getActionUIDS(), [])

    def test_register_user(self):
        """
        try to insert one user
        """
        tool = getToolByName(self.portal, SUBSCRIPTION_TOOL, None)
        rule_id = "dummy"
        email = "some@mail.com"
        result, msg = tool.registerUser(rule_id, email)
        self.assertTrue(result)
        self.assertEquals(tool.getRegisteredList(rule_id), [email])
        self.assertEquals(tool.getActionUIDS(), [rule_id])

    def test_already_registered_email(self):
        """
        try to re-register an email for the same rule id
        """
        rule = Rule()
        rule.event = IObjectAddedEvent
        rule.title = "Test rule"
        #add the rule to rule's storage
        storage = getUtility(IRuleStorage)
        chooser = INameChooser(storage)
        storage[chooser.chooseName(None, rule)] = rule
        #set the action and add it to the rule
        action = MailSubscriptionsAction()
        action.subject = "Test Rule subject"
        action.message = "Test Rule message"
        rule.actions.append(action)
        tool = getToolByName(self.portal, SUBSCRIPTION_TOOL, None)
        email = "some@mail.com"
        result, msg = tool.registerUser(action.actionUID, email)
        result2, msg2 = tool.registerUser(action.actionUID, email)
        self.assertTrue(result)
        self.assertFalse(result2)
        self.assertEquals(msg2, 'already_subscribed_error')
