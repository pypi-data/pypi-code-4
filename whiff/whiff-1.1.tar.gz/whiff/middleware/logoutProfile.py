
whiffCategory = "authorization"

whiffDoc = """
{{include "whiff_middleware/heading"}}
whiff_middleware/logoutProfile - forget profile connection
{{/include}}

The <code>whiff_middleware/listGetter</code>
middleware 
forgets a profile login.
"""

import types
# import must be absolute
from whiff.middleware import misc
from whiff import gateway

class logoutProfile(misc.utility):
    def __init__(self,
                 page,
                 userVariable="whiff.profile.user",
                 sessionResourcePath = ["session", "item"],
                 ):
        self.page = page
        self.userVariable = userVariable
        self.sessionResourcePath = sessionResourcePath
    def __call__(self, env, start_response):
        userVariable = self.param_value(self.userVariable, env)
        sessionResourcePath = self.param_json(self.sessionResourcePath, env)
        env = env.copy()
        env[userVariable] = ""
        gateway.putResource(env, sessionResourcePath+[userVariable], "")
        return self.deliver_page(self.page, env, start_response)

__middleware__ = logoutProfile
