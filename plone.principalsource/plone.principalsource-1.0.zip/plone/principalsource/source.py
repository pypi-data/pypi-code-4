from Products.CMFCore.utils import getToolByName
from plone.principalsource.term import PrincipalTerm
from z3c.formwidget.query.interfaces import IQuerySource
from zope.interface import implements
from zope.schema.interfaces import IContextSourceBinder

try:
    from zope.component.hooks import getSite
except ImportError:
    from zope.app.component.hooks import getSite


class PrincipalSource(object):
    """A queriable source for users, groups or principals (users and/or
    groups).
    
    User ids are tokens. Usernames are values. The user's fullname is the
    title, with a fallback on the name.
    
    If user ids are not ASCII strings, they'll be encoded to utf-8.
    
    If search_name is True, both user login names and full names will be
    searched. If False, only full names are searched.
    """
    implements(IQuerySource)

    def __init__(self, context, users=True, groups=True, search_name=True):
        self.context = context
        self.users = users
        self.groups = groups
        self.search_name = search_name
        
        if not self.users and not self.groups:
            raise ValueError(u"You must enable either users or groups")
        
        self.acl_users = getToolByName(context, 'acl_users', None)
        if self.acl_users is None:
            site = getSite()
            if site is not None:
                self.acl_users = getToolByName(site, 'acl_users', None)
    
    def __contains__(self, value):
        try:
            self.getTerm(value)
        except LookupError:
            return False
        else:
            return True
        
    def __iter__(self):
        """Return all users and/or groups as terms. Calling this on a site
        with many users is a very bad idea.
        """
        
        seen = set()
        for result in self._search():
            if result['id'] not in seen:
                seen.add(result['id'])
                
                # XXX: We can sometimes get bogus group results from Plone's
                # mutable properties plugin, which doesn't distinguish between
                # users and groups
                if self.users and not self.groups:
                    if self.acl_users.getUserById(result['id']) is None:
                        continue
                
                yield self._term_for_result(result)
        
    def __len__(self):
        """Return all users and/or groups as terms. Calling this on a site
        with many users is a very bad idea.
        """
        count = 0
        for item in self:
            count += 1
        return count
    
    def getTerm(self, value):
        
        results = []
        
        # There is no common attribute for user login and group id
        if self.users:
            results = self.acl_users.searchUsers(login=value, exact_match=True)
        if not results and self.groups:
            # XXX: stupidly, groups only support str ids. attempt to encode to utf-8 
            # for lack of a better policy
            value = value.encode('utf-8')
            results = self.acl_users.searchGroups(id=value, exact_match=True)
        
        if not results:
            raise LookupError(value)
        
        # There may be more than one result, and we may have gotten a subset
        # match or similar even though we asked for an exact match. Let's
        # be thorough.
        for item in results:
            term = self._term_for_result(item)
            if term.value == value:
                return term
        
        raise LookupError(value)
    
    def getTermByToken(self, token):
        # XXX: This imples the method was called with the wrong value. Tokens
        # should alwas be strings. Be lenient anyway.
        if isinstance(token, unicode):
            token = token.encode('utf-8')
        results = self._search(id=token, exact_match=True)
        if not results:
            raise LookupError(token)
        return self._term_for_result(results[0])
    
    def search(self, query_string):
        
        seen = set()
        
        if self.users:
            
            # Search by user fullname
            for result in self.acl_users.searchUsers(fullname=query_string):
                seen.add(result['id'])
                yield self._term_for_result(result)
            
            # Search by user name
            for result in self.acl_users.searchUsers(login=query_string):
                if result['id'] not in seen:
                    seen.add(result['id'])
                    yield self._term_for_result(result)
        
        if self.groups:
            
            # XXX: Stupidly, the groups plugin requires titles and ids to be
            # strings. Encode to utf-8 for lack of a better policy
            
            group_query_string = query_string.encode('utf-8')
            
            # Search by group title
            for result in self.acl_users.searchGroups(title=group_query_string):
                if result['id'] not in seen:
                    seen.add(result['id'])
                    yield self._term_for_result(result)
            
            # Search by group name
            for result in self.acl_users.searchGroups(id=group_query_string):
                if result['id'] not in seen:
                    seen.add(result['id'])
                    yield self._term_for_result(result)
    
    # Helper methods
    
    def _term_for_result(self, result_dict):
        id = result_dict['id']
        
        token = id
        if isinstance(token, unicode):
            token = token.encode('utf-8')
        
        type = result_dict.get('principal_type', 'user')
        value = result_dict.get('login', result_dict.get('groupid')) or id
        title = result_dict.get('title') or value
        
        # Attempt to get a title from the fullname if not set. Unfortunately,
        # source_users doesn't have fullname, and mutable_properties doesn't
        # match on login name or id when searching.
        
        if title == value:
            if type == 'user':
                user = self.acl_users.getUserById(id)
                if user is not None:
                    try:
                        # XXX: user.getProperty() is PlonePAS specfic
                        title = user.getProperty('fullname') or value
                    except AttributeError:
                        pass
            
            # 
            # Seems the groups source is a bit more intelligent, so we don't
            #  need this. 
            # 
            # elif type == 'group':
            #     try:
            #         group = self.acl_users.getGroupById(id)
            #         if group is not None:
            #             title = group.getProperty('title') or value
            #     except AttributeError:
            #         pass
        
        return PrincipalTerm(value=value, type=type, token=token, title=title)
    
    @property
    def _search(self):
        if self.users and self.groups:
            return self.acl_users.searchPrincipals
        elif self.users:
            return self.acl_users.searchUsers
        elif self.groups:
            return self.acl_users.searchGroups
    
# Source binders


class PrincipalSourceBinder(object):
    """Bind the principal source with either users or groups
    """
    implements(IContextSourceBinder)
    
    def __init__(self, users=True, groups=True):
        self.users = users
        self.groups = groups
    
    def __call__(self, context):
        return PrincipalSource(context, self.users, self.groups)

# Vocabulary factories (for named vocabularies)

PrincipalVocabularyFactory = PrincipalSourceBinder(users=True, groups=True)
UsersVocabularyFactory = PrincipalSourceBinder(users=True, groups=False)
GroupsVocabularyFactory = PrincipalSourceBinder(users=False, groups=True)
