
"""
Replace the page with the user id if the user has been authenticated.
If not, return the page content as the default value.
"""

whiffDoc = """
{{include "whiff_middleware/heading"}}
whiff_middleware/repoze/uid - get user name for authenticated user
{{/include}}
The <code>whiff_middleware/repoze/uid</code> gets the user name for the user
authenticated using <code>repoze.who</code>.
"""


from whiff.middleware import misc

def getUserInfo(env, key="repoze.who.userid"):
    try:
        from repoze.who.middleware import Identity
    except ImportError:
        raise ImportError, "repozeWho WHIFF middleware requires repoze.who installation [http://static.repoze.org/whodocs/]"
    identityDict = env.get("repoze.who.identity")
    if identityDict is None:
        return None
    elif not isinstance(identityDict, Identity):
        raise ValueError, "fake identity structure not permitted -- identity must be an instance of repoze.who.middleware.Identity"
    else:
        userid = identityDict.get(key)
        return userid

class repozeUserId(misc.utility):
    def __init__(self, page=None):
        self.page = page
    def __call__(self, env, start_response):
        userid = getUserInfo(env)
        if userid is not None:
            return self.deliver_page(userid, env, start_response)
        elif self.page is not None:
            # default: return the page content
            return self.deliver_page(self.page, env, start_response)
        else:
            raise ValueError, "no default, and user is not logged in"

__middleware__ = repozeUserId
