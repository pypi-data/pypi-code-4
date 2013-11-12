from datetime import date
from plone import api
from zope.interface import Invalid

from seantis.people.interfaces import IMembership, IPerson
from seantis.people.content import Membership
from seantis.people import tests


class TestMembership(tests.IntegrationTestCase):

    def test_membership_creation(self):
        with self.user('admin'):
            ms = api.content.create(
                id='test',
                type='seantis.people.membership',
                container=self.new_temporary_folder()
            )

        self.assertIs(type(ms.aq_base), Membership)

    def test_membership_range_validation(self):
        with self.user('admin'):
            ms = api.content.create(
                id='test',
                type='seantis.people.membership',
                container=self.new_temporary_folder()
            )

        ms.start, ms.end = None, None
        IMembership.validateInvariants(ms)

        ms.start, ms.end = date(2012, 1, 1), None
        IMembership.validateInvariants(ms)

        ms.start, ms.end = None, date(2012, 1, 1)
        IMembership.validateInvariants(ms)

        ms.start, ms.end = date(2012, 1, 1), date(2012, 1, 2)
        IMembership.validateInvariants(ms)

        ms.start, ms.end = date(2012, 1, 1), date(2012, 1, 1)
        IMembership.validateInvariants(ms)

        ms.start, ms.end = date(2012, 1, 2), date(2012, 1, 1)
        self.assertRaises(Invalid, IMembership.validateInvariants, ms)

    def test_membership_person_relation(self):
        person_type = self.new_temporary_type(
            behaviors=[IPerson.__identifier__]
        )

        with self.user('admin'):
            organization = self.new_temporary_folder('S.H.I.E.L.D')

            nick_fury = IPerson(api.content.create(
                title='Nick Fury',
                type=person_type.id,
                container=self.new_temporary_folder()
            ))

            api.content.create(
                title='Leader',
                type='seantis.people.membership',
                container=organization,
                person=nick_fury
            )

        self.assertEqual(len(nick_fury.memberships()), 1)

        with self.user('admin'):
            api.content.create(
                title='Leutenant',
                type='seantis.people.membership',
                container=organization,
                person=nick_fury
            )

        self.assertEqual(len(nick_fury.memberships()), 2)

    def test_membership_by_organization(self):
        person_type = self.new_temporary_type(
            behaviors=[IPerson.__identifier__]
        )

        with self.user('admin'):
            uno = self.new_temporary_folder('UNO')
            nato = self.new_temporary_folder('NATO')

            john = IPerson(api.content.create(
                title='John Doe',
                type=person_type.id,
                container=self.new_temporary_folder()
            ))

            api.content.create(
                title='Janitor',
                type='seantis.people.membership',
                container=uno,
                person=john
            )

            api.content.create(
                title='Janitor',
                type='seantis.people.membership',
                container=nato,
                person=john
            )

        self.assertEqual(len(john.memberships()), 2)
        self.assertEqual(len(john.memberships_by_organization()), 2)
        self.assertEqual(len(john.memberships_by_organization(['UNO'])), 1)
        self.assertEqual(len(john.memberships_by_organization(['NATO'])), 1)
        self.assertEqual(len(john.memberships_by_organization(['ASDF'])), 0)
