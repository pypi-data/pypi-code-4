import unittest2 as unittest

from plone import api

from ecreall.helpers.testing.workflow import BaseWorkflowTest

from collective.local.sentmail.testing import INTEGRATION, USERDEFS


admins = ('admin', 'manager')
members = ('bart', 'lisa', 'homer', 'marge', 'milhouse')
everyone = members + admins
creator = 'homer'

SENT_MAIL_PERMISSIONS = {'Access contents information': admins + (creator,),
                         'Modify portal content': admins,
                         'View': admins + (creator,),
                         }

SENT_MAILS_FOLDER_PERMISSIONS = {'Access contents information': everyone,
                                 'Add portal content': everyone,
                                 'Modify portal content': admins,
                                 'View': everyone,
                                 }


class TestSecurity(unittest.TestCase, BaseWorkflowTest):
    """We test the security (workflows)."""

    layer = INTEGRATION

    def setUp(self):
        super(TestSecurity, self).setUp()
        self.portal = self.layer['portal']
        self.mails_folder = api.content.create(type="sent_mails_folder",
                                               title=u"Sent mails",
                                               container=self.portal)
        self.login(creator)
        self.sent_mail = api.content.create(type='sent_mail',
                                            title=u'The email I have sent',
                                            body=u'Hey guys, How are you?',
                                            recipients=['lisa', 'bart'],
                                            container=self.mails_folder)

    def test_permissions_sent_mail(self):
        sent_mail = self.sent_mail
        # test sent mail permissions mapping
        self.assertCheckPermissions(sent_mail, SENT_MAIL_PERMISSIONS, USERDEFS)

    def test_permissions_sent_mails_folder(self):
        mails_folder = self.mails_folder
        # test sent mails folder permissions mapping
        self.assertCheckPermissions(mails_folder,
                                    SENT_MAILS_FOLDER_PERMISSIONS, USERDEFS)
