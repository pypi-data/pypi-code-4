# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
"""

A repoze.who plugin for Hawk HTTP Access Authentication:

    https://npmjs.org/package/hawk

"""

__ver_major__ = 0
__ver_minor__ = 2
__ver_patch__ = 0
__ver_sub__ = ""
__ver_tuple__ = (__ver_major__, __ver_minor__, __ver_patch__, __ver_sub__)
__version__ = "%d.%d.%d%s" % __ver_tuple__


import functools

from zope.interface import implements

from webob import Request, Response

from repoze.who.interfaces import IIdentifier, IAuthenticator, IChallenger
from repoze.who.utils import resolveDotted

import tokenlib

import hawkauthlib
import hawkauthlib.utils


class HawkAuthPlugin(object):
    """Plugin to implement Hawk HTTP Access Auth in repoze.who.

    This class provides an IIdentifier, IChallenger and IAuthenticator
    implementation for repoze.who.  Authentication is based on signed
    requests using the Hawk Access Authentication protocol with pre-shared
    credentials.

    The plugin can be customized with the following arguments:

        * master_secret:  a secret known only by the server, used for signing
                          Hawk id tokens in the default implementation.

        * nonce_cache:  an object implementing the same interface as
                        hawkauthlib.NonceCache.

        * decode_hawk_id:  a callable taking a Request object and Hawk id, and
                           returning the Hawk secret key and user data dict.

        * encode_hawk_id:  a callable taking a Request object and userid, and
                           returning the Hawk token id and secret key.

    """

    implements(IIdentifier, IChallenger, IAuthenticator)

    # The default value of master_secret is None, which will cause tokenlib
    # to generate a fresh secret at application startup.
    master_secret = None

    def __init__(self, master_secret=None, nonce_cache=None,
                 decode_hawk_id=None, encode_hawk_id=None):
        if master_secret is not None:
            self.master_secret = master_secret
        if nonce_cache is not None:
            self.nonce_cache = nonce_cache
        else:
            self.nonce_cache = hawkauthlib.NonceCache()
        if decode_hawk_id is not None:
            self.decode_hawk_id = decode_hawk_id
        if encode_hawk_id is not None:
            self.encode_hawk_id = encode_hawk_id

    def identify(self, environ):
        """Extract the authentication info from the request.

        We parse the Authorization header to get the Hawk auth parameters.
        If they seem sensible, we cache them in the identity to speed up
        signature checking in the authenticate() method.

        Note that this method does *not* validate the Hawk signature.
        """
        request = Request(environ)
        # Parse the Authorization header, to be cached for future use.
        params = hawkauthlib.utils.parse_authz_header(request, None)
        if params is None:
            return None
        # Extract the Hawk id.
        id = hawkauthlib.get_id(request, params=params)
        if id is None:
            return None
        # Parse the Hawk id into its data and secret key.
        try:
            key, data = self.decode_hawk_id(request, id)
        except ValueError:
            msg = "invalid Hawk id: %s" % (id,)
            return self._respond_unauthorized(request, msg)
        # Return all that data so we can using it during authentication.
        return {
            "hawkauth.id": id,
            "hawkauth.key": key,
            "hawkauth.data": data,
            "hawkauth.params": params,
        }

    def authenticate(self, environ, identity):
        """Authenticate the extracted identity.

        The identity must be a set of Hawk auth credentials extracted from
        the request.  This method checks the Hawk HMAC signature, and if valid
        extracts the user metadata from the Hawk id.
        """
        request = Request(environ)
        # Check that these are Hawk auth credentials.
        # They may not be if we're using multiple auth methods.
        id = identity.get("hawkauth.id")
        key = identity.get("hawkauth.key")
        data = identity.get("hawkauth.data")
        params = identity.get("hawkauth.params")
        if id is None or params is None or data is None or key is None:
            return None
        # Check the Hawk signature.
        if not self._check_signature(request, key, params=params):
            msg = "invalid Hawk signature"
            return self._respond_unauthorized(request, msg)
        # Find something we can use as repoze.who.userid.
        if "repoze.who.userid" not in data:
            for key in ("username", "userid", "uid", "email"):
                if key in data:
                    data["repoze.who.userid"] = data[key]
                    break
            else:
                msg = "Hawk id contains no userid"
                return self._respond_unauthorized(request, msg)
        # Update the identity with the data from the MAC id.
        identity.update(data)
        return identity["repoze.who.userid"]

    def challenge(self, environ, status, app_headers=(), forget_headers=()):
        """Challenge the user for credentials.

        This simply sends a 401 response using the WWW-Authenticate field
        as constructed by forget().
        """
        resp = Response()
        resp.status = 401
        resp.headers = self.forget(environ, {})
        for headers in (app_headers, forget_headers):
            for name, value in headers:
                resp.headers[name] = value
        resp.content_type = "text/plain"
        resp.body = "Unauthorized"
        return resp

    def remember(self, environ, identity):
        """Remember the user's identity.

        This is a no-op for this plugin; the client is supposed to remember
        its Hawk credentials and use them for all requests.
        """
        return []

    def forget(self, environ, identity):
        """Forget the user's identity.

        This simply issues a new WWW-Authenticate challenge, which should
        cause the client to forget any previously-provisioned credentials.
        """
        return [("WWW-Authenticate", "Hawk")]

    def decode_hawk_id(self, request, id):
        """Decode Hawk id into secret key and data dict.

        This method decodes the given Hawk id to give the corresponding Hawk
        secret key and dict of user data.  By default it uses the tokenlib
        library, but plugin instances may override this method with another
        callable from the config file.

        If the Hawk id is invalid then ValueError will be raised.
        """
        secret = tokenlib.get_token_secret(id, secret=self.master_secret)
        data = tokenlib.parse_token(id, secret=self.master_secret)
        return secret, data

    def encode_hawk_id(self, request, data):
        """Encode data dict into Hawk id token and secret key.

        This method is essentially the reverse of decode_hawk_id.  Given a
        dict of identity data, it encodes it into a unique Hawk id token and
        corresponding secret key.  By default it uses the tokenlib library,
        but plugin instances may override this method with another callable
        the config file.

        This method is not needed when consuming auth tokens, but is very
        handy when building them for testing purposes.
        """
        id = tokenlib.make_token(data, secret=self.master_secret)
        secret = tokenlib.get_token_secret(id, secret=self.master_secret)
        return id, secret

    def _check_signature(self, request, secret, params=None):
        """Check the request signature, using our local nonce cache."""
        return hawkauthlib.check_signature(request, secret, params=params,
                                           nonces=self.nonce_cache)

    def _respond_unauthorized(self, request, message="Unauthorized"):
        """Generate a "401 Unauthorized" error response."""
        resp = Response()
        resp.status = 401
        resp.headers = self.forget(request.environ, {})
        resp.content_type = "text/plain"
        resp.body = message
        request.environ["repoze.who.application"] = resp
        return None


def make_plugin(**kwds):
    """Make a HawkAuthPlugin using values from a .ini config file.

    This is a helper function for loading a HawkAuthPlugin via the
    repoze.who .ini config file system.  It converts its arguments from
    strings to the appropriate type then passes them on to the plugin.
    """
    master_secret = kwds.pop("master_secret", None)
    nonce_cache = _load_object_from_kwds("nonce_cache", kwds)
    decode_hawk_id = _load_function_from_kwds("decode_hawk_id", kwds)
    encode_hawk_id = _load_function_from_kwds("encode_hawk_id", kwds)
    for unknown_kwd in kwds:
        raise TypeError("unknown keyword argument: %s" % unknown_kwd)
    plugin = HawkAuthPlugin(master_secret, nonce_cache,
                            decode_hawk_id, encode_hawk_id)
    return plugin


def _load_function_from_kwds(name, kwds):
    """Load a plugin argument as a function created from the given kwds.

    This function is a helper to load and possibly curry a callable argument
    to the plugin.  It grabs the value from the dotted python name found in
    kwds[name] and checks that it is a callable.  It looks for arguments of
    the form  kwds[name_*] and curries them into the function as additional
    keyword argument before returning.
    """
    # See if we actually have the named object.
    dotted_name = kwds.pop(name, None)
    if dotted_name is None:
        return None
    func = resolveDotted(dotted_name)
    # Check that it's a callable.
    if not callable(func):
        raise ValueError("Argument %r must be callable" % (name,))
    # Curry in any keyword arguments.
    func_kwds = {}
    prefix = name + "_"
    for key in kwds.keys():
        if key.startswith(prefix):
            func_kwds[key[len(prefix):]] = kwds.pop(key)
    # Return the original function if not currying anything.
    # This is both more effient and better for unit testing.
    if func_kwds:
        func = functools.partial(func, **func_kwds)
    return func


def _load_object_from_kwds(name, kwds):
    """Load a plugin argument as an object created from the given kwds.

    This function is a helper to load and possibly instanciate an argument
    to the plugin.  It grabs the value from the dotted python name found in
    kwds[name].  If this is a callable, it looks for arguments of the form
    kwds[name_*] and calls it with them to instanciate an object.
    """
    # See if we actually have the named object.
    dotted_name = kwds.pop(name, None)
    if dotted_name is None:
        return None
    obj = resolveDotted(dotted_name)
    # Extract any arguments for the callable.
    obj_kwds = {}
    prefix = name + "_"
    for key in kwds.keys():
        if key.startswith(prefix):
            obj_kwds[key[len(prefix):]] = kwds.pop(key)
    # Call it if callable.
    if callable(obj):
        obj = obj(**obj_kwds)
    elif obj_kwds:
        raise ValueError("arguments provided for non-callable %r" % (name,))
    return obj
