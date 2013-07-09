
whiffCategory = "authorization"

whiffDoc = """
{{include "whiff_middleware/heading"}}
whiff_middleware/session - get or assign server session for client
{{/include}}

The <code>whiff_middleware/session</code>
middleware 
gets or assigns a valid session identifier by looking at a cookie
and checking the "session"
resource for validity.

The built in WHIFF session protocol
uses a session resource which works like this
<pre>
prefix+["id", oldId] --> oldId if the old Id is valid
prefix+["id", oldId] --> newId if the old Id is invalid or timed out, etc.
</pre>
The validated session id is placed in the environment
(by default at "whiff.session.id").
<p>
The "id" literal is added for extra paranoid security
to prevent an intruder
from using another resource to spoof a session id.
<p>
If the session middleware is inadvertently used several
times for the same request
it should cause no harm (except for slowing things down a bit).
"""

import types
import Cookie

# import must be absolute
from whiff.middleware import misc
from whiff import gateway

class session(misc.utility):
    def __init__(self,
                 page, # the page to return, using the Id
                 idResourcePrefix = ["session"], # path prefix for checking/setting the session (return new id if timeout or invalid)
                 cookie = "WHIFF_SESSION", # cookie name for storing the session id
                 variable = "whiff.session.id", # env variable to store the session id
                 ):
        self.page = page
        self.idResourcePrefix = idResourcePrefix
        self.cookie = cookie
        self.variable = variable
        
    def __call__(self, env, start_response):
        cookie = self.param_value(self.cookie, env)
        idResourcePrefix = self.param_json(self.idResourcePrefix, env)
        variable = self.param_value(self.variable, env)
        # extract old id from cookie
        oldId = self.getOldSessionId(env, cookie)
        # validate old id or assign new id if invalid
        newId = self.getNewSessionId(env, idResourcePrefix, oldId)
        #pr "got old/new ids", (oldId, newId)
        # place the valid session id in the environment and reset the cookie
        new_start_response = self.my_start_response_function(start_response, cookie, newId)
        env = env.copy()
        env[variable] = newId
        # deliver the wrapped page.
        return self.deliver_page(self.page, env, new_start_response)
    
    def my_start_response_function(self, start_response, cookie, newId):
        def result(status, headers):
            cookietext = "%s=%s; path=/" % (cookie, newId)
            #pr "setting cookietext", cookietext
            my_headers = headers + [( 'Set-Cookie', cookietext) ]
            #pr "headers"
            #for h in my_headers: #pr h
            #pr "end of headers"
            return start_response(status, my_headers)
        return result
    
    def getNewSessionId(self, env, idResourcePrefix, oldId):
        idResourcePath = list(idResourcePrefix) + ["id", oldId]
        result = gateway.getResource(env, idResourcePath)
        #pr "new session id is", result
        return result
    
    def getOldSessionId(self, env, cookie):
        result = None
        cookie_header = env.get("HTTP_COOKIE")
        #pr "extracting session id from header", cookie_header
        if cookie_header is not None:
            c = Cookie.SimpleCookie(cookie_header)
            if c.has_key(cookie):
                result = c[cookie].value
        #pr "found old session id", result
        return result

__middleware__ = session

    
