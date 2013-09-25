# -*- coding: utf8 -*-

import unittest2 as unittest

from plone import api

from ecreall.helpers.testing.base import BaseTest

from collective.local.sentmail.testing import INTEGRATION


class TestTypes(unittest.TestCase, BaseTest):
    """Test new content types"""

    layer = INTEGRATION

    def setUp(self):
        super(TestTypes, self).setUp()
        self.portal = self.layer['portal']
        self.mails_folder = api.content.create(type='sent_mails_folder',
                                               title=u'Sent mails',
                                               container=self.portal)

    def test_sent_mail_folder(self):
        self.assertIn('sent-mails', self.portal)

    def test_sent_mail(self):
        self.login('milhouse')
        mymail = api.content.create(type='sent_mail',
                                    title=u'The email I have sent',
                                    body=u'Hey guys, How are you today?',
                                    recipients=['lisa', 'bart'],
                                    container=self.mails_folder)
        self.assertIn('the-email-i-have-sent', self.mails_folder)
        self.assertEqual(mymail.Title(), u'The email I have sent')
        self.assertEqual(mymail.Creator(), 'milhouse')
        self.assertEqual(mymail.body, u'Hey guys, How are you today?')
        self.assertIn('lisa', mymail.recipients)
        self.assertIn('bart', mymail.recipients)
