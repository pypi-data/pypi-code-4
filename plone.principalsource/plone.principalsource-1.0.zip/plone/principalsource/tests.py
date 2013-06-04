from unittest import defaultTestLoader

from Products.Five import zcml
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup

from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory

from plone.principalsource.interfaces import IPrincipalTerm

@onsetup
def setup_product():
    import collective.discussionplus
    zcml.load_config('configure.zcml', collective.discussionplus)

setup_product()
ptc.setupPloneSite()

class TestSource(ptc.PloneTestCase):
    
    def afterSetUp(self):
        
        self.portal.portal_membership.addMember('dummy1', 'secret', ('Member',), (), 
                                                properties={'fullname': 'Test One'})
        self.portal.portal_membership.addMember('dummy2', 'secret', ('Member',), (), 
                                                properties={'fullname': 'Test Two'})
        self.portal.portal_membership.addMember('member1', 'secret', ('Member',), (), 
                                                properties={'fullname': 'Another name'})
        
        self.portal.portal_groups.addGroup('testgroup1', title='Test Group One')
        self.portal.portal_groups.addGroup('testgroup2', title='Test Group Two')
        self.portal.portal_groups.addGroup('alpha', title='Some name')
        
        principals_factory = getUtility(IVocabularyFactory, name=u"plone.principalsource.Principals")
        self.principals = principals_factory(self.portal)
        
        users_factory = getUtility(IVocabularyFactory, name=u"plone.principalsource.Users")
        self.users = users_factory(self.portal)
        
        groups_factory = getUtility(IVocabularyFactory, name=u"plone.principalsource.Groups")
        self.groups = groups_factory(self.portal)
        
    def test_contains(self):
        self.failUnless('dummy1' in self.users)
        self.failUnless('dummy2' in self.users)
        self.failUnless('member1' in self.users)
        self.failIf('testgroup1' in self.users)
        self.failIf('testgroup2' in self.users)
        self.failIf('alpha' in self.users)       
        self.failIf('test' in self.users)
        
        self.failUnless(u'dummy1' in self.users)
        self.failIf(u'test' in self.users)
        
        self.failIf('dummy1' in self.groups)
        self.failIf('dummy2' in self.groups)
        self.failIf('member1' in self.groups)
        self.failUnless('testgroup1' in self.groups)
        self.failUnless('testgroup2' in self.groups)
        self.failUnless('alpha' in self.groups)
        self.failIf('test' in self.groups)
        
        self.failUnless(u'testgroup1' in self.groups)
        self.failIf(u'test' in self.groups)
        
        self.failUnless('dummy1' in self.principals)
        self.failUnless('dummy2' in self.principals)
        self.failUnless('member1' in self.principals)
        self.failUnless('testgroup1' in self.principals)
        self.failUnless('testgroup2' in self.principals)
        self.failUnless('alpha' in self.principals)
        self.failIf('test' in self.principals)
        
        self.failUnless(u'dummy1' in self.principals)
        self.failUnless(u'testgroup1' in self.principals)
        self.failIf(u'test' in self.principals)
    
    def test_iter(self):
        
        users = [t.value for t in self.users]
        groups = [t.value for t in self.groups]
        principals = [t.value for t in self.principals]
        
        self.failUnless('dummy1' in users)
        self.failUnless('dummy2' in users)
        self.failUnless('member1' in users)
        self.failIf('testgroup1' in users)
        self.failIf('testgroup2' in users)
        self.failIf('alpha' in users)
        self.failIf('dummy' in users)
        
        self.failIf('dummy1' in groups)
        self.failIf('dummy2' in groups)
        self.failIf('member1' in groups)
        self.failUnless('testgroup1' in groups)
        self.failUnless('testgroup2' in groups)
        self.failUnless('alpha' in groups)
        self.failIf('test' in groups)
        
        self.failUnless('dummy1' in principals)
        self.failUnless('dummy2' in principals)
        self.failUnless('member1' in principals)
        self.failUnless('testgroup1' in principals)
        self.failUnless('testgroup2' in principals)
        self.failUnless('alpha' in principals)
        self.failIf('dummy' in principals)
        self.failIf('test' in principals)
        
    def test_len(self):        
        # Three test users + the PTC test use
        self.assertEquals(4, len(self.users))
        
        # Three test groups + Administrators, Reviewers and AuthenticatedUsers
        self.assertEquals(6, len(self.groups))
        
        # Both of the above
        self.assertEquals(10, len(self.principals))
        
    def test_get_term_by_value(self):
        self.assertEquals('Test One', self.users.getTerm('dummy1').title)
        self.assertEquals('dummy1', self.users.getTerm('dummy1').value)
        self.assertEquals('dummy1', self.users.getTerm('dummy1').token)
        
        self.failUnless(IPrincipalTerm.providedBy(self.users.getTerm('dummy1')))
        self.assertEquals('user', self.users.getTerm('dummy1').type)
        
        self.assertRaises(LookupError, self.users.getTerm, 'testgroup1')
        self.assertRaises(LookupError, self.users.getTerm, 'bogus')
        
        self.assertEquals('Test Group One', self.groups.getTerm('testgroup1').title)
        self.assertEquals('testgroup1', self.groups.getTerm('testgroup1').value)
        self.assertEquals('testgroup1', self.groups.getTerm('testgroup1').token)
        
        self.failUnless(IPrincipalTerm.providedBy(self.groups.getTerm('testgroup1')))
        self.assertEquals('group', self.groups.getTerm('testgroup1').type)
        
        self.assertRaises(LookupError, self.groups.getTerm, 'dummy1')
        self.assertRaises(LookupError, self.groups.getTerm, 'bogus')
        
        self.assertEquals('Test One', self.principals.getTerm('dummy1').title)
        self.assertEquals('dummy1', self.principals.getTerm('dummy1').value)
        self.assertEquals('dummy1', self.principals.getTerm('dummy1').token)
        
        self.failUnless(IPrincipalTerm.providedBy(self.principals.getTerm('dummy1')))
        self.assertEquals('user', self.principals.getTerm('dummy1').type)
        
        self.assertEquals('Test Group One', self.principals.getTerm('testgroup1').title)
        self.assertEquals('testgroup1', self.principals.getTerm('testgroup1').value)
        self.assertEquals('testgroup1', self.principals.getTerm('testgroup1').token)
        
        self.failUnless(IPrincipalTerm.providedBy(self.principals.getTerm('testgroup1')))
        self.assertEquals('group', self.principals.getTerm('testgroup1').type)
        
        self.assertRaises(LookupError, self.principals.getTerm, 'bogus')

    def test_get_term_by_value_unicode(self):
        self.assertEquals('Test One', self.users.getTerm(u'dummy1').title)
        self.assertEquals('dummy1', self.users.getTerm(u'dummy1').value)
        self.assertEquals('dummy1', self.users.getTerm(u'dummy1').token)
        
        self.failUnless(IPrincipalTerm.providedBy(self.users.getTerm(u'dummy1')))
        self.assertEquals('user', self.users.getTerm(u'dummy1').type)
        
        self.assertRaises(LookupError, self.users.getTerm, u'testgroup1')
        self.assertRaises(LookupError, self.users.getTerm, u'bogus')
        
        self.assertEquals('Test Group One', self.groups.getTerm(u'testgroup1').title)
        self.assertEquals('testgroup1', self.groups.getTerm(u'testgroup1').value)
        self.assertEquals('testgroup1', self.groups.getTerm(u'testgroup1').token)
        
        self.failUnless(IPrincipalTerm.providedBy(self.groups.getTerm(u'testgroup1')))
        self.assertEquals('group', self.groups.getTerm(u'testgroup1').type)
        
        self.assertRaises(LookupError, self.groups.getTerm, u'dummy1')
        self.assertRaises(LookupError, self.groups.getTerm, u'bogus')
        
        self.assertEquals('Test One', self.principals.getTerm(u'dummy1').title)
        self.assertEquals('dummy1', self.principals.getTerm(u'dummy1').value)
        self.assertEquals('dummy1', self.principals.getTerm(u'dummy1').token)
        
        self.failUnless(IPrincipalTerm.providedBy(self.principals.getTerm(u'dummy1')))
        self.assertEquals('user', self.principals.getTerm(u'dummy1').type)
        
        self.assertEquals('Test Group One', self.principals.getTerm(u'testgroup1').title)
        self.assertEquals('testgroup1', self.principals.getTerm(u'testgroup1').value)
        self.assertEquals('testgroup1', self.principals.getTerm(u'testgroup1').token)
        
        self.failUnless(IPrincipalTerm.providedBy(self.principals.getTerm(u'testgroup1')))
        self.assertEquals('group', self.principals.getTerm(u'testgroup1').type)
        
        self.assertRaises(LookupError, self.principals.getTerm, u'bogus')

    def test_get_term_by_token(self):

        self.assertEquals('Test One', self.users.getTermByToken('dummy1').title)
        self.assertEquals('dummy1', self.users.getTermByToken('dummy1').value)
        self.assertEquals('dummy1', self.users.getTermByToken('dummy1').token)
        
        self.failUnless(IPrincipalTerm.providedBy(self.users.getTermByToken('dummy1')))
        self.assertEquals('user', self.users.getTermByToken('dummy1').type)
        
        self.assertRaises(LookupError, self.users.getTermByToken, 'testgroup1')
        self.assertRaises(LookupError, self.users.getTermByToken, 'bogus')
        
        self.assertEquals('Test Group One', self.groups.getTermByToken('testgroup1').title)
        self.assertEquals('testgroup1', self.groups.getTermByToken('testgroup1').value)
        self.assertEquals('testgroup1', self.groups.getTermByToken('testgroup1').token)
        
        self.failUnless(IPrincipalTerm.providedBy(self.groups.getTermByToken('testgroup1')))
        self.assertEquals('group', self.groups.getTermByToken('testgroup1').type)
        
        self.assertRaises(LookupError, self.groups.getTermByToken, 'dummy1')
        self.assertRaises(LookupError, self.groups.getTermByToken, 'bogus')
        
        self.assertEquals('Test One', self.principals.getTermByToken('dummy1').title)
        self.assertEquals('dummy1', self.principals.getTermByToken('dummy1').value)
        self.assertEquals('dummy1', self.principals.getTermByToken('dummy1').token)
        
        self.failUnless(IPrincipalTerm.providedBy(self.principals.getTermByToken('dummy1')))
        self.assertEquals('user', self.principals.getTermByToken('dummy1').type)
        
        self.assertEquals('Test Group One', self.principals.getTermByToken('testgroup1').title)
        self.assertEquals('testgroup1', self.principals.getTermByToken('testgroup1').value)
        self.assertEquals('testgroup1', self.principals.getTermByToken('testgroup1').token)
        
        self.failUnless(IPrincipalTerm.providedBy(self.principals.getTermByToken('testgroup1')))
        self.assertEquals('group', self.principals.getTermByToken('testgroup1').type)
        
        self.assertRaises(LookupError, self.principals.getTermByToken, 'bogus')
    
    # Search users
    
    def test_search_users_login(self):
        
        # Search finds multiple users
        results = list(self.users.search('dummy'))
        self.assertEquals(2, len(results))

    def test_search_users_login_unicode(self):
        
        # Search finds multiple users
        results = list(self.users.search(u'dummy'))
        self.assertEquals(2, len(results))
    
    def test_search_users_nogroups(self):
        
        # User search does not include groups
        results = list(self.users.search('testgroup'))
        self.assertEquals(0, len(results))
    
    def test_search_users_caseinsensitive(self):
        
        # Search is case insensitive
        results = list(self.users.search('MEMBER'))
        self.assertEquals(1, len(results))
    
    def test_search_users_nomatch(self):
    
        # Search returns nothing if nothing is matched
        results = list(self.users.search('bogus'))
        self.assertEquals(0, len(results))
    
    def test_search_users_fullname_or_username(self):
        
        # Search can search full name or username
        results = list(self.users.search('member'))
        self.assertEquals(1, len(results))
        
        results = list(self.users.search('Another name'))
        self.assertEquals(1, len(results))
    
    # Search groups
    
    def test_search_groups_id(self):
        
        # Search finds multiple users
        results = list(self.groups.search('testgroup'))
        self.assertEquals(2, len(results))

    def test_search_groups_id_unicode(self):
        
        # Search finds multiple users
        results = list(self.groups.search(u'testgroup'))
        self.assertEquals(2, len(results))
    
    def test_search_groups_name_unicode(self):
        
        # Search finds multiple users
        results = list(self.groups.search(u'Test Group'))
        self.assertEquals(2, len(results))
    
    def test_search_groups_nousers(self):
        
        # User search does not include groups
        results = list(self.groups.search('dummy'))
        self.assertEquals(0, len(results))
    
    def test_search_groups_caseinsensitive(self):
        
        # Search is case insensitive
        results = list(self.groups.search('ALPHA'))
        self.assertEquals(1, len(results))
    
    def test_search_groups_nomatch(self):
    
        # Search returns nothing if nothing is matched
        results = list(self.groups.search('bogus'))
        self.assertEquals(0, len(results))
    
    def test_search_groups_title_or_name(self):
        # Search can search full name or username
        results = list(self.groups.search('alpha'))
        self.assertEquals(1, len(results))
        
        results = list(self.groups.search('Some name'))
        self.assertEquals(1, len(results))
        
    # Search principals
    
    def test_search_principals_login_or_id(self):

        # Search finds multiple users and groups
        results = list(self.principals.search('test'))
        # includes test_user_1_, two test users and two test groups
        self.assertEquals(5, len(results))
    
    def test_search_principals_caseinsensitive(self):
        
        # Search is case insensitive
        results = list(self.principals.search('ALPHA'))
        self.assertEquals(1, len(results))
        
        results = list(self.principals.search('MEMBER'))
        self.assertEquals(1, len(results))
    
    def test_search_principals_nomatch(self):
    
        # Search returns nothing if nothing is matched
        results = list(self.principals.search('bogus'))
        self.assertEquals(0, len(results))
    
    def test_search_principals_title_or_name(self):
        
        # Search can search full name or username
        results = list(self.principals.search('member'))
        self.assertEquals(1, len(results))
        
        results = list(self.principals.search('Another'))
        self.assertEquals(1, len(results))
        
        # or group id or group name 
        results = list(self.principals.search('alpha'))
        self.assertEquals(1, len(results))
        
        results = list(self.principals.search('Some name'))
        self.assertEquals(1, len(results))

def test_suite():
    return defaultTestLoader.loadTestsFromName(__name__)