"""
allow listed users to view the page.  Others view failure page
"""

whiffDoc = """
{{include "whiff_middleware/heading"}}
whiff_middleware/repoze/allow -- allow listed authenticated users to view the page or application
{{/include}}
The <code>whiff_middleware/repoze/allow</code> middleware checks whether the user is authenticated
and allows only listed authenticated users to view the <code>page</code> argument.
The <code>users</code> argument may be a JSON sequence of user names or <code>true</code> (to
indicate any authenticated users) or <code>null</code> to indicate that the page is intended
only for logged out users.
"""

from whiff.middleware import misc
from uid import getUserInfo

class repozeAllow(misc.utility):
    def __init__(self,
                 users, # json/list of user names (True/true means any logged in user; None/null means not logged in)
                 page,
                 failurePage
                 ):
        self.users = users
        self.page = page
        self.failurePage = failurePage
    def __repr__(self):
        return "repozeAllow(%s, %s, %s)"% (repr(self.users), repr(self.page), repr(self.failurePage))
    def __call__(self, env, start_response):
        uid = getUserInfo(env)
        users = self.param_json(self.users, env)
        success = False
        if users is None:
            success = (uid is None)
        elif users is True:
            success = (uid is not None)
        else:
            success = (uid in users)
        if success:
            #pr "allow returns success", start_response, self.page
            return self.deliver_page(self.page, env, start_response)
        else:
            #pr "allow returns failure"
            return self.deliver_page(self.failurePage, env, start_response)

__middleware__ = repozeAllow
