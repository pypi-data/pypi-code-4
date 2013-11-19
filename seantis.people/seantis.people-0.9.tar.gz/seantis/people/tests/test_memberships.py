from contextlib import contextmanager
from datetime import date

from zope.component import getGlobalSiteManager, getAdapters
from zope.interface import Interface

from plone import api
from plone.uuid.interfaces import IUUID

from seantis.people import tests
from seantis.people.interfaces import IMembershipSource, IPerson


class TestAdapter(object):

    def __init__(self, context):
        self.context = context


class Membership(object):

    def __init__(self, person, role=None, start=None, end=None):
        self.person = person
        self.role = role
        self.start = start
        self.end = end


class TestMemberships(tests.IntegrationTestCase):

    def register_membership_source(self, adapter, interface, name):
        gsm = getGlobalSiteManager()
        gsm.registerAdapter(
            factory=adapter, required=(interface,), name=name,
            provided=IMembershipSource
        )

    def unregister_membership_source(self, adapter, interface, name):
        gsm = getGlobalSiteManager()
        gsm.unregisterAdapter(required=(interface,), name=name,
            provided=IMembershipSource
        )

    @contextmanager
    def custom_source(self, source):
        self.register_membership_source(source, Interface, 'custom-source')
        yield
        self.unregister_membership_source(source, Interface, 'custom-source')

    def get_test_person(self):
        person_type = self.new_temporary_type(
            behaviors=[IPerson.__identifier__]
        )

        with self.user('admin'):
            person = api.content.create(
                title='person',
                type=person_type.id,
                container=self.new_temporary_folder()
            )

        return person

    def test_membership_adapter_registration(self):

        class Source(TestAdapter):

            def memberships(self, person=None):
                pass

        with self.custom_source(Source):

            folder = self.new_temporary_folder()

            adapters = [
                name for name, source in
                getAdapters((folder, ), IMembershipSource)
            ]

            self.assertEqual(
                adapters, ['zodb-membership-source', 'custom-source']
            )

        adapters = [
            name for name, source in
            getAdapters((folder, ), IMembershipSource)
        ]
        self.assertEqual(adapters, ['zodb-membership-source'])

    def test_membership_organizations(self):

        person = self.get_test_person()
        organization = self.new_temporary_folder()

        class Source(TestAdapter):

            def memberships(self, person=None):
                return {
                    IUUID(organization): [
                        Membership(person)
                    ]
                }

        with self.custom_source(Source):
            self.assertEqual(IPerson(person).organizations(), [
                organization.title
            ])

    def test_active_memberships(self):
        person = self.get_test_person()
        organization = self.new_temporary_folder()

        class Source(TestAdapter):

            def memberships(self, person=None):
                return {
                    IUUID(organization): [
                        Membership(person),
                        Membership(person, end=date(2012, 1, 1))
                    ]
                }

        with self.custom_source(Source):
            memberships = IPerson(person).memberships()[IUUID(organization)]
            self.assertEqual(len(memberships), 2)

            active = IPerson(person).active_memberships(memberships)
            self.assertEqual(len(active), 1)

    def test_current_role(self):
        person = self.get_test_person()
        organization = self.new_temporary_folder()

        class Source(TestAdapter):

            def memberships(self, person=None):
                return {
                    IUUID(organization): [
                        Membership(person, 'president'),
                        Membership(person, 'secretary', end=date(2012, 1, 1))
                    ]
                }

        with self.custom_source(Source):
            memberships = IPerson(person).memberships()[IUUID(organization)]
            role = IPerson(person).current_role(memberships)

            self.assertEqual(role, 'president')
