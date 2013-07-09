"""
    Simple and stupid WSGI authorization demo middleware based on cookies and log in forms.
    This is "stupid" because the cookie shows the username and
    password in clear text, which is not a very secure way of doing
    things.  It's also stupid because it will not allow the successPage to have
    GET or POST parameters.

    Don't use this for serious security.  It might be useful for easy
    but not-too-important use, or for demos.
"""

whiffCategory = "authorization"

whiffDoc = """
{{include "whiff_middleware/heading"}}
whiff_middleware/insecureAuthorize - simple minded authorization
{{/include}}

    This is a simple
    and stupid WSGI authorization demo middleware based on cookies and log in forms.
    This is "stupid" because the cookie shows the username and
    password in clear text, which is not a very secure way of doing
    things.  It's also stupid because it will not allow the successPage to have
    GET or POST parameters.

    Don't use this for serious security.  It might be useful for easy
    but not-too-important use, or for demos.

"""

import Cookie
import cgi
from whiff import resolver
from whiff import whiffenv

# import must be absolute
from whiff.middleware import misc

DEFAULT_USER_VAR = "whiff.middleware.auth_user"

class InsecureAuthorization(misc.utility):
    """
    The "authorizations" require should be a dictionary of name-->password.
    The loginPage return GET parameters USER and PASSWORD when filled in.
    The successPage should be any page which requires no GET or POST parameters.
    """
    user = None
    password = None
    def __init__(self, successPage, loginPage, authorizations, uservar=DEFAULT_USER_VAR):
        """
        SuccessPage is a page to present if login is successful.
        LoginPage is page to present to request a login.
        authorizations is a dictionary mapping user names to passwords.
        """
        #pr "InsecureAuthorization"
        #pr "   successPage=", successPage
        #pr "   loginPage=", loginPage
        #pr "   authorizations=", authorizations
        self.successPage = successPage
        self.loginPage = loginPage
        self.authorizations = authorizations
        self.server_start_response = None
        self.user = None
        self.password = None
        self.uservar = uservar
    def my_start_response(self, status, headers):
        "intercept the start_response: set the userInfo cookie entry if appropriate and start the server response"
        my_headers = headers
        if self.user is not None and self.password is not None:
            # include a Set-Cookie header
            cookie_value = "UserInfo="+self.user+"/"+self.password+"; path=/"
            #pr "setting cookie value", cookie_value
            my_headers = headers + [ ('Set-Cookie', cookie_value) ]
        # tell the server to start the response
        self.server_start_response(status, my_headers)
    def __call__(self, env, start_response):
        # remember the start_response because my_start_response might need it
        self.server_start_response = start_response
        # look for GET parameters USER and PASSWORD
        env = resolver.process_cgi(env, parse_cgi=True)
        query_dict = env[whiffenv.CGI_DICTIONARY]
        if query_dict.has_key("USER") and query_dict.has_key("PASSWORD"):
            self.user = query_dict["USER"][0]
            self.password = query_dict["PASSWORD"][0]
            #pr "got user and password from cgi data"
        # if that didn't work, look for a cookie entry UserInfo with value of form USER/PASSWORD
        if self.user is None:
            cookie_header = env.get("HTTP_COOKIE")
            if cookie_header is not None:
                #pr "AUTH USING COOKIE", repr(cookie_header)
                c = Cookie.SimpleCookie(cookie_header)
                if c.has_key("UserInfo"):
                    entry = c["UserInfo"].value
                    if "/" in entry:
                        [self.user, self.password] = entry.split("/", 2)
                        #pr "got user and password from cookie data"
        # check whether the user is known and the password matches
        auth = self.param_json(self.authorizations, env)
        #pr "FOUND USER AND PASSWORD", (self.user, self.password)
        if auth.has_key(self.user) and auth[self.user]==self.password:
            #pr "authorization succeeded"
            # the user is authorized! deliver the successPage (but set a cookie using my_start_response)
            env = env.copy()
            # store the authorization user name in the environment
            uservar = self.param_value(self.uservar, env)
            env[uservar] = self.user
            # return the successpage
            return self.successPage(env, self.my_start_response)
        # otherwise the user is not authorized: deliver the login page
        #pr "authorization failed", self.user, self.password
        #pr "in", auth
        return self.loginPage(env, self.my_start_response)

__middleware__ = InsecureAuthorization
