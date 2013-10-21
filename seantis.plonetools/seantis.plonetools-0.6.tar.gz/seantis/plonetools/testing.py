import unittest2 as unittest
import uuid

from plone.dexterity import fti
from contextlib import contextmanager

from zope import event
from zope.traversing.interfaces import BeforeTraverseEvent

from zope.component import getSiteManager
from Products.CMFPlone.tests.utils import MockMailHost
from Products.MailHost.interfaces import IMailHost

from plone.testing import z2
from plone import api

from collective.betterbrowser import new_browser

from seantis.plonetools import tools


def install_mailhost(portal, mailhost):
    portal.MailHost = mailhost

    sm = getSiteManager(context=portal)
    sm.unregisterUtility(provided=IMailHost)
    sm.registerUtility(mailhost, provided=IMailHost)


def install_mock_mailhost(portal, from_address='noreply@example.com'):
    portal._original_mailhost = portal.MailHost
    portal.email_from_address = from_address

    install_mailhost(portal, MockMailHost('MailHost'))


def uninstall_mock_mailhost(portal):
    if hasattr(portal, '_original_mailhost'):
        install_mailhost(portal, portal._original_mailhost)


class TestCase(unittest.TestCase):
    """ Testcase which can be used with different Seantis plone modules. """

    def setUp(self):

        self.app = self.layer['app']
        self.portal = self.layer['portal']

        self.temporary_folders = []
        self.temporary_types = []

        install_mock_mailhost(self.portal)

        # remove all test event subscribers
        event.subscribers = [
            e for e in event.subscribers if type(e) != TestEventSubscriber
        ]

        self.current_user = None

        # setup manually the correct browserlayer, see:
        # https://dev.plone.org/ticket/11673
        event.notify(BeforeTraverseEvent(self.portal, self.request))

    def tearDown(self):
        uninstall_mock_mailhost(self.portal)
        self.remove_temporary_folders()
        self.remove_temporary_types()
        self.logout()

    @property
    def request(self):
        return self.layer['request']

    @property
    def mailhost(self):
        return self.portal.MailHost

    def login(self, user):
        if user == 'admin':
            acl = self.app['acl_users']
        else:
            acl = self.portal['acl_users']

        z2.login(acl, user)
        self.current_user = user

    def logout(self):
        z2.logout()
        self.current_user = None

    @contextmanager
    def user(self, user):
        """ Use as follows:

        with self.user('admin'):
            # do admin stuff

        """
        old_user = self.current_user
        self.login(user)

        yield

        self.logout()
        if old_user:
            self.login(old_user)

    def new_browser(self):
        return new_browser(self.layer)

    def subscribe(self, eventclass):
        subscriber = TestEventSubscriber(eventclass)
        event.subscribers.append(subscriber)
        return subscriber

    def new_temporary_folder(self, title=None):
        with self.user('admin'):
            folder = api.content.create(
                type='Folder',
                title=title or uuid.uuid4().hex,
                container=self.portal
            )

            self.temporary_folders.append(folder)

            return folder

    def remove_temporary_folders(self):
        with self.user('admin'):
            for folder in self.temporary_folders:
                api.content.delete(obj=folder)

    def new_temporary_type(self, **kwargs):
        """ Creates a new dexterity type and registers it with plone. Use it
        to easily test behaviors.

        """
        with self.user('admin'):
            new_type = tools.add_new_dexterity_type(uuid.uuid4().hex, **kwargs)
            self.temporary_types.append(new_type)

            return new_type

    def remove_temporary_types(self):
        types = api.portal.get_tool('portal_types')

        with self.user('admin'):
            for temp_type in self.temporary_types:
                types._delObject(temp_type.id)

                fti.unregister(temp_type)


class TestEventSubscriber(object):

    def __init__(self, eventclass):
        self.eventclass = eventclass
        self.event = None

    def __call__(self, event):
        if type(event) is self.eventclass:
            self.event = event

    def was_fired(self):
        return self.event is not None

    def reset(self):
        self.event = None
