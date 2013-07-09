whiffDoc = """
{{include "whiff_middleware/heading"}}
whiff_middleware/newProfile - create a profile object
{{/include}}

The <code>whiff_middleware/newProfile</code> middleware
establishes a new user profile.
"""

whiffCategory = "authorization"


import types
# import must be absolute
from whiff.middleware import misc
from whiff import gateway

class newProfile(misc.utility):
    def __init__(self,
                 page, # page to deliver when done and successful
                 elsePage, # page to deliver when failed
                 user,
                 password,
                 password2,
                 sessionResourcePath = ["session", "item"],
                 userVariable="whiff.profile.user", # if this is set to None when done, then failure
                 passwordVariable="whiff.profile.password",
                 errorVariable="whiff.profile.error",
                 profileResourcePrefix=["profile"], # prefix for accessing profile information
                 ):
        self.page = page
        self.elsePage = elsePage
        self.user = user
        self.password = password
        self.password2 = password2
        self.sessionResourcePath = sessionResourcePath
        self.userVariable = userVariable
        self.passwordVariable = passwordVariable
        self.profileResourcePrefix = profileResourcePrefix
        self.errorVariable = errorVariable
    def __call__(self, env, start_response):
        user = self.param_value(self.user, env)
        password = self.param_value(self.password, env)
        password2 = self.param_value(self.password2, env)
        userVariable = self.param_value(self.userVariable, env)
        passwordVariable = self.param_value(self.passwordVariable, env)
        errorVariable = self.param_value(self.errorVariable, env)
        sessionResourcePath = self.param_json(self.sessionResourcePath, env)
        profileResourcePrefix = self.param_json(self.profileResourcePrefix, env)
        env = env.copy()
        # test that passwords match
        #pr "establishing new profile", (user, password, password2, userVariable, passwordVariable, sessionResourcePath)
        if password!=password2:
            # failure
            env[errorVariable] = "passwords do not match"
            env[userVariable] = None
            env[passwordVariable] = None
        else:
            # establish a new profile
            identity = gateway.getResource(env, profileResourcePrefix+["new", user, password])
            if identity:
                # record the profile information in the session and environment
                gateway.putResource(env, sessionResourcePath+[userVariable], user)
                gateway.putResource(env, sessionResourcePath+[passwordVariable], password)
                env[userVariable] = user
                env[passwordVariable] = password
            else:
                # failure
                env[errorVariable] = "username invalid or in use"
                env[userVariable] = None
                env[passwordVariable] = None                
        # deliver the page
        if env[userVariable]:
            return self.deliver_page(self.page, env, start_response)
        else:
            return self.deliver_page(self.elsePage, env, start_response)

__middleware__ = newProfile
