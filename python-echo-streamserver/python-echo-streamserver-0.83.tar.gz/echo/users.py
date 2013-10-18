""" Users API

Echo Users API is designed for providing interface for working with user identities along with core permission information.

The core data element of this API is a User Account Record. The user account is created automatically when the user logs in for the first time. 

The user account contains one or more identities (E.g. Twitter, Facebook, Acme Widgets) which are represented by identity URLs. A URL is considered to be a valid identity URL if it is either well-known (recognized by Social Graph Node Mapper) or is an OpenID.

User Accounts are stored in a namespace - essentially each namespace is a different user database.

One can think of user accounts as boxes where business cards (identities) are put. When a new user gets logged in to the system, a new box is allocated and the user's business cards (identities) are placed into it. Echo allows to add multiple identities to an account, but removing identities or binding them to a different account is not yet supported.

User properties (roles, markers etc) are associated with accounts, not identities. However it is possible to reference a user account in API methods by referencing any of the identities bound to the account. This is conceptually equivalent to checking every single box looking for a particular business card and then marking the box appropriately.
""" 
from echo.core_api import EchoClient, StreamServerError

try:
    import json
except ImportError:
    import simplejson as json

import logging

USER_SUBJECTS = [ 'roles', 'state', 'markers', 'poco' ]

# ======================================================================

class Client(EchoClient):
    def get(self, identity_url, raise_not_found=False):
        """ Fetch user information. """
        param_d = {
            'identityURL': identity_url,
        }
        r = {}
        try:
            r = self._send_request('users/get', param_d, http_post=False)
        except StreamServerError, e:
            # Trap 'not_found', but re-raise everything else.
            if (not raise_not_found) and (e.errorCode == 'not_found'):
                pass
            else:
                raise
        return r

    def update(self, identity_url, subject, content):
        """ Update (or insert new) user information in the subject area to the value of content. """
        if subject not in USER_SUBJECTS:
            raise ValueError("Users API must update a valid subject %r, not %r" % (USER_SUBJECTS, subject))
        # Convert content to a JSON document.
        param_d = {
            'identityURL': identity_url,
            'subject': subject,
            'content': json.dumps(content),
        }
        return self._send_request('users/update', param_d, http_post=True)

    def whoami(self, session_id):
        """ Retrieve currently logged in user information. """
        param_d = {
            'appkey': self._account._appkey,
            'sessionID': session_id,
        }
        return self._send_request('users/whoami', param_d, http_post=False)

# Module-level client exposes API
# ======================================================================

def get(identity_url, raise_not_found=False):
    """ Fetch user information. """
    return Client.get_client().get(identity_url, raise_not_found=raise_not_found)

def update(identity_url, subject, content):
    """ Update (or insert new) user information in the subject area to the value of content. """
    return Client.get_client().update(identity_url, subject, content)

def whoami(session_id):
    """ Retrieve currently logged in user information. """
    return Client.get_client().whoami(session_id)

# ======================================================================

if __name__ == "__main__":
    from pprint import pprint

    # Get and show an existing user's indetityURL.
    user_d = get("http://connect-uat.nj.com/user/amurphre/index.html", raise_not_found=True)
    pprint(user_d, indent=4)

    # Show the user JSON's poco account #0.
    account_d = user_d['poco']['entry']['accounts'][0]
    print
    pprint(account_d, indent=4)

    # Convert that poco account #0 into a User object.
    # User classes are not part of the API, since they vary.
    class PoCoUser(object):
        def __init__(self, user_json):
            try:
                account_d = user_d['poco']['entry']['accounts'][0]
                for k,v in account_d.items():
                    setattr(self,  k, v)
            except Exception, e:
                raise

        def __str__(self):
            return '(%s) "%s" %s' % (self.username, self.displayName, self.identityUrl)

    # Show a new PoCoUser.
    print
    u = PoCoUser(user_d)
    print "PoCoUser dir():"
    pprint(dir(u), indent=4)
    print
    print "User: %s" % str(u)

