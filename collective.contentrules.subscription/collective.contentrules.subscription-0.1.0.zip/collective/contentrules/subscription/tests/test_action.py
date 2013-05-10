# -*- coding: UTF-8 -*-
from base import BaseTestCase
from collective.contentrules.subscription import SUBSCRIPTION_TOOL
from collective.contentrules.subscription.actions.mail import MailSubscriptionsAction
from collective.contentrules.subscription.actions.mail import MailSubscriptionsAddForm, MailSubscriptionsEditForm
from collective.contentrules.subscription.testing import CONTENTRULESSUBSCRIPTION_FUNCTIONAL_TESTING
from email import message_from_string
from email.Message import Message
from plone.app.contentrules.rule import Rule
from plone.contentrules.engine.interfaces import IRuleStorage
from plone.contentrules.rule.interfaces import IRuleAction, IExecutable
from Products.CMFCore.utils import getToolByName
from Products.MailHost.interfaces import IMailHost
from Products.MailHost.MailHost import MailHost
from zope.component import getUtility, getMultiAdapter, getSiteManager
from zope.component.interfaces import IObjectEvent
from zope.interface import implements
# basic test structure copied from plone.app.contentrules test_action_mail.py


class DummyEvent(object):
    implements(IObjectEvent)

    def __init__(self, object):
        self.object = object


class DummyMailHost(MailHost):
    meta_type = 'Dummy Mail Host'

    def __init__(self, id):
        self.id = id
        self.sent = []

    def _send(self, mfrom, mto, messageText, *args, **kw):
        msg = message_from_string(messageText)
        self.sent.append(msg)


class TestMailAction(BaseTestCase):

    layer = CONTENTRULESSUBSCRIPTION_FUNCTIONAL_TESTING

    def setUp(self):
        """
        """
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.tool = getToolByName(self.portal, SUBSCRIPTION_TOOL, None)
        self.markRequestWithLayer()
        self.portal.invokeFactory('Folder', 'target', title=unicode('Folder', 'utf-8'))
        self.portal.target.invokeFactory('Document', 'd1', title=unicode('Document', 'utf-8'))
        self.folder = self.portal.target

    def testRegistered(self):
        element = getUtility(IRuleAction, name='plone.actions.MailSubscriptions')
        self.assertEquals('plone.actions.MailSubscriptions', element.addview)
        self.assertEquals('edit', element.editview)
        self.assertEquals(None, element.for_)
        self.assertEquals(IObjectEvent, element.event)

    def testInvokeAddView(self):
        element = getUtility(IRuleAction, name='plone.actions.MailSubscriptions')
        storage = getUtility(IRuleStorage)
        storage[u'foo'] = Rule()
        rule = self.portal.restrictedTraverse('++rule++foo')

        adding = getMultiAdapter((rule, self.portal.REQUEST), name='+action')
        addview = getMultiAdapter((adding, self.portal.REQUEST),
                                  name=element.addview)
        self.failUnless(isinstance(addview, MailSubscriptionsAddForm))

        addview.createAndAdd(data={'subject': 'My Subject',
                                   'source': 'foo@mail.com',
                                   'message': 'Hey, Oh!'})

        e = rule.actions[0]
        self.failUnless(isinstance(e, MailSubscriptionsAction))
        self.assertEquals('My Subject', e.subject)
        self.assertEquals('foo@mail.com', e.source)
        self.assertEquals('Hey, Oh!', e.message)

    def testInvokeEditView(self):
        element = getUtility(IRuleAction, name='plone.actions.MailSubscriptions')
        e = MailSubscriptionsAction()
        editview = getMultiAdapter((e, self.folder.REQUEST),
                                   name=element.editview)
        self.failUnless(isinstance(editview, MailSubscriptionsEditForm))


    def testExecuteNoSource(self):
        sm = getSiteManager(self.portal)
        sm.unregisterUtility(provided=IMailHost)
        dummyMailHost = DummyMailHost('dMailhost')
        sm.registerUtility(dummyMailHost, IMailHost)
        e = MailSubscriptionsAction()
        e.message = 'Document created !'
        e.subject = "subject"
        self.tool.registerUser(e.actionUID, "member1@dummy.org")
        ex = getMultiAdapter((self.folder, e, DummyEvent(self.folder.d1)),
                             IExecutable)
        self.assertRaises(ValueError, ex)
        # if we provide a site mail address this won't fail anymore
        sm.manage_changeProperties({'email_from_name': 'The Big Boss',
                                    'email_from_address': 'manager@portal.be',
                                    })
        ex()
        self.failUnless(isinstance(dummyMailHost.sent[0], Message))
        mailSent = dummyMailHost.sent[0]
        self.assertEqual('text/plain; charset="utf-8"',
                        mailSent.get('Content-Type'))
        self.assertEqual("member1@dummy.org", mailSent.get('To'))
        self.assertEqual("The Big Boss <manager@portal.be>",
                         mailSent.get('From'))
        self.assertEqual("Document created !",
                         mailSent.get_payload(decode=True))
