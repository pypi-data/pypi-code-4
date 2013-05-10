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
from zope.component import queryUtility
from plone.registry.interfaces import IRegistry
from collective.z3cform.norobots.browser.interfaces import INorobotsWidgetSettings


class TestSubscriptionView(BaseTestCase):

    layer = CONTENTRULESSUBSCRIPTION_FUNCTIONAL_TESTING

    def setUp(self):
        """
        """
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.markRequestWithLayer()
        # Creating empty value for ACTUAL_URL to prevent KeyError
        self.request['ACTUAL_URL'] = ''
        app = self.layer['app']
        #set some things
        #create a test user with email
        self.acl_users = getToolByName(self.portal, 'acl_users')
        self.acl_users.userFolderAddUser('user1', 'secret', ['Member'], [])
        self.user1 = self.acl_users.getUser('user1')
        self.user1.setProperties(email='user1@mail.com')
        #now set some rules
        self.tool = getToolByName(self.portal, SUBSCRIPTION_TOOL, None)
        self.portal_url = self.portal.absolute_url()
        self.browser = Browser(app)
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
        #set one only norobots question
        registry = queryUtility(IRegistry)
        settings = registry.forInterface(INorobotsWidgetSettings, check=False)
        settings.questions = (u'What is 4 + 4 ?::8',)
        transaction.commit()

    def test_subscription_view(self):
        """
        test if there is subscription view
        """
        view = getMultiAdapter((self.portal, self.request), name="notify-subscribe")
        view = view.__of__(self.portal)
        self.failUnless(view())

    def test_check_required_fields(self):
        """
        """
        self.browser.open("%s/@@notify-subscribe" % self.portal_url)
        #check if we are anonymous and we are in right view
        self.assertTrue("Log in" in self.browser.contents)
        self.assertTrue("Subscribe to site notifications" in self.browser.contents)
        #submit form without filling any field
        self.browser.getControl(name='form.buttons.subscribe').click()
        #check if the view doesn't returns ok message
        self.assertFalse("You are subscribed succesfully." in self.browser.contents)
        #check if all three required fields returns an error
        self.assertEquals(self.browser.contents.count("Required input is missing."), 3)

    def test_check_wrong_email(self):
        """
        """
        self.browser.open("%s/@@notify-subscribe" % self.portal_url)
        #check if we are anonymous and we are in right view
        self.assertTrue("Log in" in self.browser.contents)
        self.assertTrue("Subscribe to site notifications" in self.browser.contents)
        #set form fields
        email_field = self.browser.getControl(name="form.widgets.email")
        self.assertEqual(email_field.value, '')
        email_field.value = "wrong_value"
        rules_list = self.browser.getControl(name="form.widgets.rules:list")
        self.assertEquals(len(rules_list.options), 3)
        #we want to subscribe for first two rules
        subscription_rules = rules_list.options[:2]
        rules_list.value = subscription_rules
        #set a wrong value
        self.browser.getControl(name="form.widgets.norobots").value = '8'
        self.browser.getControl(name='form.buttons.subscribe').click()
        #check if the view returns ok message
        self.assertFalse("You are subscribed succesfully." in self.browser.contents)
        self.assertTrue("You entered an invalid email address." in self.browser.contents)

    def test_check_wrong_norobots(self):
        """
        """
        self.browser.open("%s/@@notify-subscribe" % self.portal_url)
        #check if we are anonymous and we are in right view
        self.assertTrue("Log in" in self.browser.contents)
        self.assertTrue("Subscribe to site notifications" in self.browser.contents)
        #set form fields
        email_field = self.browser.getControl(name="form.widgets.email")
        self.assertEqual(email_field.value, '')
        email_field.value = "test@email.com"
        rules_list = self.browser.getControl(name="form.widgets.rules:list")
        self.assertEquals(len(rules_list.options), 3)
        #we want to subscribe for first two rules
        subscription_rules = rules_list.options[:2]
        rules_list.value = subscription_rules
        #set a wrong value
        self.browser.getControl(name="form.widgets.norobots").value = 'wrong'
        self.browser.getControl(name='form.buttons.subscribe').click()
        #check if the view returns ok message
        self.assertFalse("You are subscribed succesfully." in self.browser.contents)
        self.assertTrue("You entered a wrong answer, please answer the new question below." in self.browser.contents)

    def test_subscribe_anonymous(self):
        """
        """
        self.browser.open("%s/@@notify-subscribe" % self.portal_url)
        #check if we are anonymous and we are in right view
        self.assertTrue("Log in" in self.browser.contents)
        self.assertTrue("Subscribe to site notifications" in self.browser.contents)
        #set form fields
        email_field = self.browser.getControl(name="form.widgets.email")
        self.assertEqual(email_field.value, '')
        email_field.value = "test@email.com"
        rules_list = self.browser.getControl(name="form.widgets.rules:list")
        self.assertEquals(len(rules_list.options), 3)
        #we want to subscribe for first two rules
        subscription_rules = rules_list.options[:2]
        rules_list.value = subscription_rules
        self.browser.getControl(name="form.widgets.norobots").value = '8'
        self.browser.getControl(name='form.buttons.subscribe').click()
        #check if the view returns ok message
        self.assertTrue("You are subscribed succesfully." in self.browser.contents)
        #check if the tool is correctly set
        self.assertEquals(len(self.tool.getActionUIDS()), 2)
        self.assertEquals(self.tool.getRegisteredList(subscription_rules[0]), ["test@email.com", ])
        self.assertEquals(self.tool.getRegisteredList(subscription_rules[1]), ["test@email.com", ])

    def test_subscribe_user_with_email(self):
        """
        """
        self.browser.addHeader('Authorization', 'Basic %s:%s' % ("user1", "secret",))
        self.browser.open("%s/@@notify-subscribe" % self.portal_url)
        #check if we are anonymous and we are in right view
        self.assertFalse("Log in" in self.browser.contents)
        #set form fields
        email_field = self.browser.getControl(name="form.widgets.email")
        self.assertEqual(email_field.value, 'user1@mail.com')
        rules_list = self.browser.getControl(name="form.widgets.rules:list")
        self.assertEquals(len(rules_list.options), 3)
        #we want to subscribe for first two rules
        subscription_rules = rules_list.options[:2]
        rules_list.value = subscription_rules
        self.browser.getControl(name="form.widgets.norobots").value = '8'
        self.browser.getControl(name='form.buttons.subscribe').click()
        #check if the view returns ok message
        self.assertTrue("You are subscribed succesfully." in self.browser.contents)
        #check if the tool is correctly set
        self.assertEquals(len(self.tool.getActionUIDS()), 2)
        self.assertEquals(self.tool.getRegisteredList(subscription_rules[0]), ["user1@mail.com", ])
        self.assertEquals(self.tool.getRegisteredList(subscription_rules[1]), ["user1@mail.com", ])
        self.browser.getLink("Log out").click()

    def test_subscribe_twice(self):
        """
        """
        self.browser.open("%s/@@notify-subscribe" % self.portal_url)
        #check if we are anonymous and we are in right view
        self.assertTrue("Log in" in self.browser.contents)
        #set form fields
        email_field = self.browser.getControl(name="form.widgets.email")
        self.assertEqual(email_field.value, '')
        email_field.value = "test@email.com"
        rules_list = self.browser.getControl(name="form.widgets.rules:list")
        self.assertEquals(len(rules_list.options), 3)
        #we want to subscribe for first two rules
        subscription_rule = rules_list.options[:1]
        rules_list.value = subscription_rule
        self.browser.getControl(name="form.widgets.norobots").value = '8'
        self.browser.getControl(name='form.buttons.subscribe').click()
        #check if the view returns ok message
        self.assertTrue("You are subscribed succesfully." in self.browser.contents)
        #check if the tool is correctly set
        self.assertEquals(len(self.tool.getActionUIDS()), 1)
        self.assertEquals(self.tool.getRegisteredList(subscription_rule[0]), ["test@email.com", ])
        #re-set form fields with same values
        email_field = self.browser.getControl(name="form.widgets.email")
        email_field.value = "test@email.com"
        rules_list = self.browser.getControl(name="form.widgets.rules:list")
        subscription_rule = rules_list.options[:1]
        rules_list.value = subscription_rule
        self.browser.getControl(name="form.widgets.norobots").value = '8'
        self.browser.getControl(name='form.buttons.subscribe').click()
        #check if the view doesn't returns ok message
        self.assertFalse("You are subscribed succesfully." in self.browser.contents)
        self.assertTrue('The given email is already present for "first rule"' in self.browser.contents)
        #check if the tool isn't changed
        self.assertEquals(len(self.tool.getActionUIDS()), 1)
        self.assertEquals(self.tool.getRegisteredList(subscription_rule[0]), ["test@email.com", ])
