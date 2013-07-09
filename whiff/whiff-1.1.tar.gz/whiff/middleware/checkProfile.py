"""
Validate user profile.
"""

whiffCategory = "authorization"

whiffDoc = """
{{include "whiff_middleware/heading"}}
whiff_middleware/checkProfile - check user profile
{{/include}}

The <code>whiff_middleware/checkProfile</code>
middleware determines whether the user has an assigned
user profile resource and delivers a success page if so
or if not delivers a failure page.  If the invocation provides
the user and password parameters, the
<code>whiff_middleware/checkProfile</code> middleware uses
those values to attempt to locate the profile and cache
the profile in the session object.

{{include "example"}}
{{using targetName}}checkProfile{{/using}}
{{using page}}

{{include "whiff_middleware/checkProfile"}}
    {{using page}}
        CONGRATULATIONS! YOU HAVE A PROFILE!
    {{/using}}
    {{using failure}}
        I'M SORRY YOU DON'T HAVE A PROFILE ASSIGNED!
    {{/using}}
{{/include}}

{{/using}}
{{/include}}

"""

import types
# import must be absolute
from whiff.middleware import misc
from whiff import gateway

class checkProfile(misc.utility):
    def __init__(self,
                 page, # page to return if profile is ok
                 failure=None, # page to return if profile is not assigned or bad
                 user=None, # user id for login
                 password=None, # password for login
                 sessionResourcePath = ["session", "item"],
                 userVariable="whiff.profile.user",
                 passwordVariable="whiff.profile.password",
                 errorVariable="whiff.profile.error",
                 profileResourcePrefix=["profile"], # prefix for accessing profile information
                 ):
        self.page = page
        self.failure = failure
        self.user = user
        self.password = password
        self.userVariable = userVariable
        self.passwordVariable = passwordVariable
        self.errorVariable = errorVariable
        self.sessionResourcePath = sessionResourcePath
        self.profileResourcePrefix = profileResourcePrefix
        
    def __call__(self, env, start_response):
        # find user and password, put them in environment
        storeSession = True
        env = env.copy()
        userVariable = self.param_value(self.userVariable, env)
        passwordVariable = self.param_value(self.passwordVariable, env)
        errorVariable = self.param_value(self.errorVariable, env)
        profileResourcePrefix = self.param_json(self.profileResourcePrefix, env)
        sessionResourcePath = self.param_json(self.sessionResourcePath, env)
        user = password = None
        if self.user:
            user = self.param_value(self.user, env)
            user = user.strip()
            #pr "user from params", user
        if not user and sessionResourcePath:
            user = gateway.getResource(env, sessionResourcePath+[userVariable])
            user = user.strip()
            #pr "user from session", user
            if user:
                storeSession = False
        if not user:
            user = env.get(userVariable)
            #pr "user from environment", user
        if user:
            #pr "assigning", (userVariable, user)
            env[userVariable] = user                        
        if self.password:
            password = self.param_value(self.password, env)
            password = password.strip()
            #pr "password from params", password
        if not password and  sessionResourcePath:
            password = gateway.getResource(env, sessionResourcePath+[passwordVariable])
            #pr "password from session", password
        if not password:
            password = env.get(passwordVariable)
            #pr "password from environment",password
        if password:
            #pr "assigning", (passwordVariable, password)
            env[passwordVariable] = password
        #pr "checking profile", (profileResourcePrefix, user, password)
        profileValid = self.checkProfile(env, profileResourcePrefix, user, password)
        #pr "got", profileValid
        if profileValid:
            if storeSession:
                gateway.putResource(env, sessionResourcePath+[userVariable], user)
                gateway.putResource(env, sessionResourcePath+[passwordVariable], password)                
            # profile ok... success
            #pr "check profile returns success", self.page
            return self.deliver_page(self.page, env, start_response)
        # if we get here, we failed :(
        if user or password:
            #pr "setting error"
            env[errorVariable] = "invalid user name or password"
        #pr "check profile returns failure", self.failure
        if self.failure:
            return self.deliver_page(self.failure, env, start_response)
        else:
            start_response("200 OK", [('Content-Type', 'text/plain')])
            return ["login required"]
    
    def checkProfile(self, env, profileResourcePrefix, user, password):
        #pr "checking profile", profileResourcePrefix, user, password
        resourcePath = profileResourcePrefix+["id", user]
        #pr "GETTING PATH", resourcePath
        result = gateway.getResource(env, resourcePath, False)
        #pr "RESULT: checkProfile path", resourcePath, "got result", result
        return result

__middleware__ = checkProfile
