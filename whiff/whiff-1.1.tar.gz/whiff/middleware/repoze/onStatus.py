"""
allow users to view page.  non-users view failure page
"""

whiffDoc = """
{{include "whiff_middleware/heading"}}
whiff_middleware/repoze/onStatus - deliver different responses to logged in or logged out user
{{/include}}
The <code>whiff_middleware/repoze/onStatus</code> middleware tests whether the user has
been authenticated by <code>repoze.who</code> -- authenticated users receive the <code>loggedIn</code>
page, and non-authenticated users receive the <code>unknown</code> page.
"""

from whiff.middleware import misc
from uid import getUserInfo

class repozeOnStatus(misc.utility):
    def __init__(self,
                 loggedIn,
                 unknown,
                 ):
        self.loggedIn = loggedIn
        self.unknown = unknown
    def __call__(self, env, start_response):
        uid = getUserInfo(env)
        if uid is None:
            return self.deliver_page(self.unknown, env, start_response)
        else:
            return self.deliver_page(self.loggedIn, env, start_response)

__middleware__ = repozeOnStatus
