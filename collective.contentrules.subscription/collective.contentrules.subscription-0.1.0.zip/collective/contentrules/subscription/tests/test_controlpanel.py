# -*- coding: utf-8 -*-
from base import BaseTestCase
from collective.contentrules.subscription.testing import CONTENTRULESSUBSCRIPTION_FUNCTIONAL_TESTING
from Products.CMFCore.utils import getToolByName
from plone.app.contentrules.rule import Rule
from collective.contentrules.subscription import SUBSCRIPTION_TOOL
from zope.app.container.interfaces import IObjectAddedEvent, INameChooser
from plone.contentrules.engine.interfaces import IRuleStorage
from zope.component import getUtility, getMultiAdapter
from collective.contentrules.subscription.actions.mail import MailSubscriptionsAction
from plone.app.testing import logout
from plone.app.testing import SITE_OWNER_NAME, SITE_OWNER_PASSWORD
from plone.testing.z2 import Browser
import transaction


class TestControlpanel(BaseTestCase):

    layer = CONTENTRULESSUBSCRIPTION_FUNCTIONAL_TESTING

    def setUp(self):
        """
        """
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        # Creating empty value for ACTUAL_URL to prevent KeyError
        self.request['ACTUAL_URL'] = ''
        self.markRequestWithLayer()

    def test_controlpanel_view(self):
        """
        test if there is settings view
        """
        view = getMultiAdapter((self.portal, self.request), name="contentrules-subscription-controlpanel")
        view = view.__of__(self.portal)
        self.failUnless(view())

    def test_controlpanel_view_protected(self):
        """
        test if the settings view is protected
        """
        from AccessControl import Unauthorized
        logout()
        self.assertRaises(Unauthorized, self.portal.restrictedTraverse, '@@contentrules-subscription-controlpanel')


class TestControlpanelFunctionalities(BaseTestCase):

    layer = CONTENTRULESSUBSCRIPTION_FUNCTIONAL_TESTING

    def setUp(self):
        """
        """
        app = self.layer['app']
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.tool = getToolByName(self.portal, SUBSCRIPTION_TOOL, None)
        self.markRequestWithLayer()
        self.portal_url = self.portal.absolute_url()
        self.browser = Browser(app)
        self.browser.addHeader('Authorization', 'Basic %s:%s' % (SITE_OWNER_NAME, SITE_OWNER_PASSWORD,))
        #Create some rules
        for x in ["first", "second", "third"]:
            #set some rules
            rule = Rule()
            rule.event = IObjectAddedEvent
            rule.title = "%s rule" % x
            #add the rules to rule's storage
            storage = getUtility(IRuleStorage)
            chooser = INameChooser(storage)
            storage[chooser.chooseName(None, rule)] = rule
            #set the action and add it to the rule
            action = MailSubscriptionsAction()
            action.subject = "Test %s action subject" % x
            rule.actions.append(action)
            email1 = "some@mail.com"
            email2 = "foo@mail.com"
            self.tool.registerUser(action.actionUID, email1)
            self.tool.registerUser(action.actionUID, email2)
        transaction.commit()

    def test_check_right_list(self):
        """
        """
        self.browser.open("%s/@@contentrules-subscription-controlpanel" % self.portal_url)
        self.assertTrue(u"first rule" in self.browser.contents)
        self.assertTrue(u"second rule" in self.browser.contents)
        self.assertTrue(u"third rule" in self.browser.contents)

    def test_remove_subscription(self):
        """
        """
        self.browser.open("%s/@@contentrules-subscription-controlpanel" % self.portal_url)
        action_id = self.tool.getActionUIDS()[0]
        action_subscriptions = self.browser.getControl(name="%s:list" % action_id)
        self.assertEquals(len(action_subscriptions.value), 2)
        self.assertEquals(action_subscriptions.value, self.tool.getRegisteredList(action_id))
        subscription = action_subscriptions.getControl(value='foo@mail.com')
        subscription.selected = False
        self.browser.getControl(name='form.button.Update').click()
        self.assertTrue(u"Subscriptions updated" in self.browser.contents)
        action_subscriptions = self.browser.getControl(name="%s:list" % action_id)
        self.assertEquals(len(action_subscriptions.value), 1)
        self.assertEquals(action_subscriptions.value, self.tool.getRegisteredList(action_id))
