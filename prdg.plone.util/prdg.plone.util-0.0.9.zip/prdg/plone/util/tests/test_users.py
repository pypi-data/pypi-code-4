#coding=utf8
from base import BaseTestCase
from prdg.plone.util import users
import unittest
import pickle


class UsersTestCase(BaseTestCase):
    """Test the users module."""

    def test_get_password(self):
        password = 'pass1'
        member_id = 'user1'
        self.membership.addMember(member_id, password, ['Member'], '')

        result = users.get_password(self.portal, member_id)
        self.failUnless((result is None) or (result == password))

    def test_create_dict_from_member(self):
        member_id = 'user1'
        self.membership.addMember(
            member_id,
            'pass1',
            ['Member', 'Reviewer'],
            '',
            {'fullname': 'Barack Obama', 'email': 'barack@whitehouse.gov'}
        )
        member = self.membership.getMemberById(member_id)

        d = users.create_dict_from_member_obj(self.portal, member)
        self.failUnless('fullname' in d)
        self.fail_unless_dict_and_member_matches(d, member)

        d2 = users.create_dict_from_member_id(self.portal, member_id)
        self.failUnless('fullname' in d)
        self.fail_unless_dict_and_member_matches(d2, member)

        self.failUnlessEqual(d, d2)

    def test_pickle(self):
        """
        Assert the dicts created by create_dict_from_member() are pickable.
        """
        member_id = 'user1'
        self.membership.addMember(
            member_id,
            'pass1',
            ['Member', 'Reviewer'],
            '',
            {'fullname': 'Barack Obama', 'email': 'barack@whitehouse.gov'}
        )
        member = self.membership.getMemberById(member_id)

        d = users.create_dict_from_member_obj(self.portal, member)
        self.failUnless('fullname' in d)
        self.fail_unless_dict_and_member_matches(d, member)

        pickle_str = pickle.dumps(d)
        d2 = pickle.loads(pickle_str)
        self.failUnlessEqual(d, d2)

    def test_create_member_from_dict(self):
        d = {
            'id': 'user3',
            'password': 'nananana',
            'roles': ('Member', 'Reviewer'),
            'email': 'email@email.com.br',
        }

        member = users.create_member_from_dict(self.portal, d)
        self.failUnless(member.getProperty('email'))
        self.fail_unless_dict_and_member_matches(d, member)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(UsersTestCase))
    return suite
