# -*- coding: utf8 -*-

import unittest2 as unittest

from zope.event import notify

from plone import api
from plone.app.textfield.value import RichTextValue

from ecreall.helpers.testing.base import BaseTest

from collective.local.sendto.events import MailSentEvent

from collective.local.sentmail.testing import INTEGRATION


class TestSubscribers(unittest.TestCase, BaseTest):
    """Test new subscribers"""

    layer = INTEGRATION

    def setUp(self):
        super(TestSubscribers, self).setUp()
        self.portal = self.layer['portal']

    def test_mail_sent(self):
        sent_mails_folder = self.portal['sent-mails']
        from collective.local.sendto.interfaces import ISendToAvailable
        self.assertTrue(ISendToAvailable.providedBy(sent_mails_folder))
        bart = api.user.get('bart')
        homer = api.user.get('homer')
        self.login('lisa')
        event = MailSentEvent(subject=u"Mail subject",
                              body=u"Mail <strong>body</strong> text",
                              recipients=[bart, homer])
        notify(event)
        self.assertIn('mail-subject', sent_mails_folder)
        mail = sent_mails_folder['mail-subject']
        self.assertEqual(u"Mail subject", mail.Title())
        rich_text_body = RichTextValue(raw=u"Mail <strong>body</strong> text",
                                       mimeType="text/html",
                                       outputMimeType="text/x-html-safe",
                                       encoding='utf-8')
        self.assertEqual(rich_text_body.output, event.body)
        self.assertEqual('lisa', mail.Creator())
        self.assertIn('bart', mail.recipients)
        self.assertIn('homer', mail.recipients)
