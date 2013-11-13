#coding=utf8
import unittest
from ..testing import FUNCTIONAL_TESTING
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_ROLES
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import setRoles
from plone.testing.z2 import Browser
from plone import api
from Acquisition import aq_parent
from Products.Archetypes.Field import FileField, TextField
from operator import eq
from prdg.plone.util.structure import objs_to_paths
from prdg.plone.util.users import get_password
from prdg.plone.util.utils import get_workflow_state, ofs_file_equal
from plone.app.testing import TEST_USER_PASSWORD
import os.path
from tempfile import gettempdir

ROLES_TO_REMOVE = set(['Authenticated'])


class BaseTestCase(unittest.TestCase):

    layer = FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.browser = Browser(self.layer['app'])

        setRoles(self.portal, TEST_USER_ID, TEST_USER_ROLES + ['Manager'])
        self.folder = api.content.create(
            container=self.portal,
            type='Folder',
            id='folder-test',
            title='Folder Test',
        )

        self.portal_url = self.portal.absolute_url()
        self.folder_url = self.folder.absolute_url()
        self.acl_users = self.portal.acl_users
        self.workflow = self.portal.acl_users.portal_workflow
        self.error_log = self.portal.error_log
        self.css = self.portal.portal_css
        self.skins = self.portal.portal_skins
        self.types = self.portal.portal_types
        self.factory = self.portal.portal_factory
        self.workflow = self.portal.portal_workflow
        self.properties = self.portal.portal_properties
        self.mail_host = self.portal.MailHost
        self.qi = self.portal.portal_quickinstaller
        self.putils = self.portal.plone_utils
        self.registration = self.portal.portal_registration
        self.membership = self.portal.portal_membership

    def fail_unless_dict_and_obj_matches(self, d, obj):
        """
        Check if dict matches object.

        More specifically: iterate through all items in d and check if they
        matches with attributes of obj. Special keys like _path, owner_userid,
        etc are tested too.
        """
        def fail_unless_equal(obj_value, eq_func=eq):
            self.failUnless(
                eq_func(value, obj_value),
                'field: %s. d = %s, obj = %s' % (name, value, obj_value)
            )

        d = dict(d)  # Dont't modify the dict.
        container = aq_parent(obj)

        # Required keys.
        (name, value) = ('container id', container.getId())
        fail_unless_equal(obj.getPhysicalPath()[-2])

        (name, value) = ('portal_type', d.pop('portal_type'))
        fail_unless_equal(obj.portal_type)

        (name, value) = ('id', d.pop('id'))
        fail_unless_equal(obj.getId())

        for (name, value) in d.iteritems():
            field = obj.getField(name)

            if name.startswith('ref:'):
                name = name.split(':')[1]
                value = set(value)
                field = obj.getField(name)

                referenced_objs = field.get(obj, aslist=True)
                referenced_paths = set(objs_to_paths(referenced_objs))
                fail_unless_equal(referenced_paths)

            elif name == '_path':
                fail_unless_equal(obj.getPhysicalPath()[2:])

            elif name == 'owner_userid':
                fail_unless_equal(self.putils.getOwnerName(obj))

            elif name == 'workflow_dest_state':
                fail_unless_equal(get_workflow_state(obj))

            elif name == 'local_roles':
                obj_local_roles = getattr(obj, '__ac_local_roles__', {})
                local_roles = value
                for (user_id, roles) in local_roles.iteritems():
                    value = (user_id, roles)
                    fail_unless_equal((user_id, obj_local_roles.get(user_id)))

            elif isinstance(field, FileField) and (not isinstance(field, TextField)):
                fail_unless_equal(field.get(obj), ofs_file_equal)

            else:
                fail_unless_equal(field.get(obj))

    def fail_unless_dict_and_member_matches(self, d, member):
        d = dict(d)
        member_id = member.getId()

        self.failUnlessEqual(d.pop('id'), member_id)

        password = d.pop('password', None)
        real_password = get_password(self.portal, member_id)
        self.failUnless(
            (real_password is None) or (password == real_password)
        )

        roles = set(d.pop('roles')) - ROLES_TO_REMOVE
        real_roles = set(member.getRoles()) - ROLES_TO_REMOVE
        self.failUnlessEqual(roles, real_roles)

        for (k, v) in d.iteritems():
            self.failUnlessEqual(v, member.getProperty(k))

    def login_browser(self, name=TEST_USER_NAME, password=TEST_USER_PASSWORD):
        """Login an user in self.browser."""
        self.browser.open(self.portal_url + '/login_form')
        self.browser.getControl(name='__ac_name').value = name
        self.browser.getControl(name='__ac_password').value = password
        self.browser.getControl(name='submit').click()

    def dump_browser_contents(self, filename='a.html'):
        """
        Create a file inside the default temp directory with the contents
        of the current page.
        """
        path = os.path.join(gettempdir(), filename)
        with open(path, 'w') as f:
            f.write(self.browser.contents)

    def fail_if_errors_in_error_log(self):
        entries = self.error_log.getLogEntries()
        if not entries:
            return

        entries_str = [
            '%s: %s' % (e['type'], e['value'][:70])
            for e in entries
        ]

        msg = 'Error log entries:\n' + '\n'.join(entries_str)
        self.fail(msg)
