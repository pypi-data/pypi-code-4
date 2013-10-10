#!/usr/bin/env python
#
# Copyright 2010 Facebook
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""Python client library for the Facebook Platform.

This client library is designed to support the Graph API and the
official Facebook JavaScript SDK, which is the canonical way to
implement Facebook authentication. Read more about the Graph API at
http://developers.facebook.com/docs/api. You can download the Facebook
JavaScript SDK at http://github.com/facebook/connect-js/.

If your application is using Google AppEngine's webapp framework, your
usage of this module might look like this:

user = facebook.get_user_from_cookie(self.request.cookies, key, secret)
if user:
    graph = facebook.GraphAPI(user["access_token"])
    profile = graph.get_object("me")
    friends = graph.get_connections("me", "friends")

"""

import hashlib
import hmac
import base64
import sys
try:
    from urllib.parse import parse_qs
except ImportError:
    from urlparse import parse_qs

try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode

from geventhttpclient import HTTPClient
from geventhttpclient.url import URL

# Find a JSON parser
try:
    import ujson as json
except ImportError:
    try:
        import simplejson as json
    except ImportError:
        import json
_parse_json = json.loads

if sys.version_info[0] == 3:
    basestring = (str,)
else:
    basestring = (str, unicode)


FACEBOOK_URL = URL('https://graph.facebook.com/')
FACEBOOK_FQL_URL = URL('https://api.facebook.com/')


class GraphAPI(object):
    """A client for the Facebook Graph API.

    See http://developers.facebook.com/docs/api for complete
    documentation for the API.

    The Graph API is made up of the objects in Facebook (e.g., people,
    pages, events, photos) and the connections between them (e.g.,
    friends, photo tags, and event RSVPs). This client provides access
    to those primitive types in a generic way. For example, given an
    OAuth access token, this will fetch the profile of the active user
    and the list of the user's friends:

       graph = facebook.GraphAPI(access_token)
       user = graph.get_object("me")
       friends = graph.get_connections(user["id"], "friends")

    You can see a list of all of the objects and connections supported
    by the API at http://developers.facebook.com/docs/reference/api/.

    You can obtain an access token via OAuth or by using the Facebook
    JavaScript SDK. See
    http://developers.facebook.com/docs/authentication/ for details.

    If you are using the JavaScript SDK, you can use the
    get_user_from_cookie() method below to get the OAuth access token
    for the active user from the cookie saved by the SDK.

    """
    def __init__(self, access_token=None, timeout=None):
        self.access_token = access_token
        self.timeout = timeout

    def get_object(self, id, **args):
        """Fetchs the given object from the graph."""
        return self.request(id, args)

    def get_objects(self, ids, **args):
        """Fetchs all of the given object from the graph.

        We return a map from ID to object. If any of the IDs are
        invalid, we raise an exception.
        """
        args["ids"] = ",".join(ids)
        return self.request("", args)

    def get_connections(self, id, connection_name, **args):
        """Fetchs the connections for given object."""
        return self.request(id + "/" + connection_name, args)

    def put_object(self, parent_object, connection_name, **data):
        """Writes the given object to the graph, connected to the given parent.

        For example,

            graph.put_object("me", "feed", message="Hello, world")

        writes "Hello, world" to the active user's wall. Likewise, this
        will comment on a the first post of the active user's feed:

            feed = graph.get_connections("me", "feed")
            post = feed["data"][0]
            graph.put_object(post["id"], "comments", message="First!")

        See http://developers.facebook.com/docs/api#publishing for all
        of the supported writeable objects.

        Certain write operations require extended permissions. For
        example, publishing to a user's feed requires the
        "publish_actions" permission. See
        http://developers.facebook.com/docs/publishing/ for details
        about publishing permissions.

        """
        assert self.access_token, "Write operations require an access token"
        return self.request(parent_object + "/" + connection_name,
                            post_args=data)

    def put_wall_post(self, message, attachment={}, profile_id="me"):
        """Writes a wall post to the given profile's wall.

        We default to writing to the authenticated user's wall if no
        profile_id is specified.

        attachment adds a structured attachment to the status message
        being posted to the Wall. It should be a dictionary of the form:

            {"name": "Link name"
             "link": "http://www.example.com/",
             "caption": "{*actor*} posted a new review",
             "description": "This is a longer description of the attachment",
             "picture": "http://www.example.com/thumbnail.jpg"}

        """
        return self.put_object(profile_id, "feed", message=message,
                               **attachment)

    def put_comment(self, object_id, message):
        """Writes the given comment on the given post."""
        return self.put_object(object_id, "comments", message=message)

    def put_like(self, object_id):
        """Likes the given post."""
        return self.put_object(object_id, "likes")

    def delete_object(self, id):
        """Deletes the object with the given ID from the graph."""
        return self.request(id, post_args={"method": "delete"})

    def delete_request(self, user_id, request_id):
        """Deletes the Request with the given ID for the given user."""
        path = URL('/%s_%s' % (request_id, user_id))
        path['access_token'] = self.access_token
        http = HTTPClient.from_url(
            FACEBOOK_URL, connection_timeout=self.timeout)
        resp = http.delete(path.request_uri)
        content = resp.read()
        content = _parse_json(content)
        if content and isinstance(content, dict) and content.get("error"):
            raise GraphAPIError(content["error"])
        http.close()
        return content

    def put_photo(self, image, message=None, album_id=None, **kwargs):
        """Uploads an image using multipart/form-data.

        image=File like object for the image
        message=Caption for your image
        album_id=None posts to /me/photos which uses or creates and uses
        an album for your application.

        """
        raise NotImplemented()

    # based on: http://code.activestate.com/recipes/146306/
    def _encode_multipart_form(self, fields):
        """Encode files as 'multipart/form-data'.

        Fields are a dict of form name-> value. For files, value should
        be a file object. Other file-like objects might work and a fake
        name will be chosen.

        Returns (content_type, body) ready for httplib.HTTP instance.

        """
        raise NotImplemented()

    def request(self, path, args=None, post_args=None):
        """Fetches the given path in the Graph API.

        We translate args to a valid query string. If post_args is
        given, we send a POST request to the given path with the given
        arguments.

        """
        http = HTTPClient.from_url(
            FACEBOOK_URL, connection_timeout=self.timeout)
        args = args or {}
        if not path.startswith('/'):
            path = '/%s' % path
        path = URL(path)
        if self.access_token:
            if post_args is not None:
                post_args["access_token"] = self.access_token
            else:
                args["access_token"] = self.access_token
        path.query.update(args)  # add GET params to url
        try:
            if not post_args:
                resp = http.get(path.request_uri)
            else:
                resp = http.post(path.request_uri, body=urlencode(post_args))
            content = resp.read()
            if 'image' in resp['content-type']:
                content = {
                    'data': content,
                    'mime-type': resp['content-type'],
                    'url': path.request_uri
                }
            else:
                content = _parse_json(content)
        except Exception as e:
            raise GraphAPIError(e)
        finally:
            http.close()
        if content and isinstance(content, dict) and content.get("error"):
            raise GraphAPIError(content["error"])
        return content

    def fql(self, query, args=None, post_args=None):
        """FQL query.

        Example query: "SELECT affiliations FROM user WHERE uid = me()"

        """
        http = HTTPClient.from_url(
            FACEBOOK_FQL_URL, connection_timeout=self.timeout)
        args = args or {}
        if self.access_token:
            if post_args is not None:
                post_args["access_token"] = self.access_token
            else:
                args["access_token"] = self.access_token
        """Check if query is a dict and
           use the multiquery method
           else use single query
        """
        if not isinstance(query, basestring):
            args["queries"] = query
            fql_method = 'fql.multiquery'
        else:
            args["query"] = query
            fql_method = 'fql.query'
        path = URL('/method/%s' % fql_method)
        args["format"] = "json"
        path.query.update(args)  # add GET params to url
        try:
            if not post_args:
                resp = http.get(path.request_uri)
            else:
                resp = http.post(path.request_uri, body=urlencode(post_args))
            content = resp.read()
            content = _parse_json(content)
        except Exception as e:
            raise GraphAPIError(e)
        finally:
            http.close()
        if content and isinstance(content, dict) and content.get("error"):
            raise GraphAPIError(content["error"])
        return content

    def extend_access_token(self, app_id, app_secret):
        """
        Extends the expiration time of a valid OAuth access token. See
        <https://developers.facebook.com/roadmap/offline-access-removal/
        #extend_token>
        """
        http = HTTPClient.from_url(
            FACEBOOK_URL, connection_timeout=self.timeout)
        args = {
            "client_id": app_id,
            "client_secret": app_secret,
            "grant_type": "fb_exchange_token",
            "fb_exchange_token": self.access_token,
        }
        path = URL('/oauth/access_token')
        path.query.update(args)  # add GET params to url
        try:
            resp = http.get(path.request_uri)
            content = resp.read()
            query_str = parse_qs(content)
            if "access_token" in query_str:
                result = {"access_token": query_str["access_token"][0]}
                if "expires" in query_str:
                    result["expires"] = query_str["expires"][0]
                return result
            content = _parse_json(content)
        except Exception as e:
            raise GraphAPIError(e)
        finally:
            http.close()
        if content and isinstance(content, dict) and content.get("error"):
            raise GraphAPIError(content["error"])
        return content


class GraphAPIError(Exception):
    def __init__(self, result):
        #Exception.__init__(self, message)
        #self.type = type
        self.result = result
        try:
            self.type = result["error_code"]
        except:
            self.type = ""

        # OAuth 2.0 Draft 10
        try:
            self.message = result["error_description"]
        except:
            # OAuth 2.0 Draft 00
            try:
                self.message = result["error"]["message"]
            except:
                # REST server style
                try:
                    self.message = result["error_msg"]
                except:
                    self.message = result

        Exception.__init__(self, self.message)


def get_user_from_cookie(cookies, app_id, app_secret):
    """Parses the cookie set by the official Facebook JavaScript SDK.

    cookies should be a dictionary-like object mapping cookie names to
    cookie values.

    If the user is logged in via Facebook, we return a dictionary with
    the keys "uid" and "access_token". The former is the user's
    Facebook ID, and the latter can be used to make authenticated
    requests to the Graph API. If the user is not logged in, we
    return None.

    Download the official Facebook JavaScript SDK at
    http://github.com/facebook/connect-js/. Read more about Facebook
    authentication at
    http://developers.facebook.com/docs/authentication/.

    """
    cookie = cookies.get("fbsr_" + app_id, "")
    if not cookie:
        return None
    parsed_request = parse_signed_request(cookie, app_secret)
    if not parsed_request:
        return None
    try:
        result = get_access_token_from_code(parsed_request["code"], "",
                                            app_id, app_secret)
    except GraphAPIError:
        return None
    result["uid"] = parsed_request["user_id"]
    return result


def parse_signed_request(signed_request, app_secret):
    """ Return dictionary with signed request data.

    We return a dictionary containing the information in the
    signed_request. This includes a user_id if the user has authorised
    your application, as well as any information requested.

    If the signed_request is malformed or corrupted, False is returned.

    """
    try:
        encoded_sig, payload = list(map(str, signed_request.split('.', 1)))

        sig = base64.urlsafe_b64decode(encoded_sig + "=" *
                                       ((4 - len(encoded_sig) % 4) % 4))
        data = base64.urlsafe_b64decode(payload + "=" *
                                        ((4 - len(payload) % 4) % 4))
    except IndexError:
        # Signed request was malformed.
        return False
    except TypeError:
        # Signed request had a corrupted payload.
        return False

    data = _parse_json(data)
    if data.get('algorithm', '').upper() != 'HMAC-SHA256':
        return False

    # HMAC can only handle ascii (byte) strings
    # http://bugs.python.org/issue5285
    app_secret = app_secret.encode('ascii')
    payload = payload.encode('ascii')

    expected_sig = hmac.new(app_secret,
                            msg=payload,
                            digestmod=hashlib.sha256).digest()
    if sig != expected_sig:
        return False

    return data


def auth_url(app_id, canvas_url, perms=None, **kwargs):
    url = "https://www.facebook.com/dialog/oauth?"
    kvps = {'client_id': app_id, 'redirect_uri': canvas_url}
    if perms:
        kvps['scope'] = ",".join(perms)
    kvps.update(kwargs)
    return url + urlencode(kvps)


def get_access_token_from_code(code, redirect_uri, app_id, app_secret):
    """Get an access token from the "code" returned from an OAuth dialog.

    Returns a dict containing the user-specific access token and its
    expiration date (if applicable).

    """
    args = {
        "code": code,
        "redirect_uri": redirect_uri,
        "client_id": app_id,
        "client_secret": app_secret,
    }
    # We would use GraphAPI.request() here, except for that the fact
    # that the response is a key-value pair, and not JSON.

    url = URL("https://graph.facebook.com/oauth/access_token")
    url.query.update(args)
    http = HTTPClient.from_url(url)
    resp = http.get(url.request_uri)
    content = resp.read()
    query_str = parse_qs(content)

    if "access_token" in query_str:
        result = {"access_token": query_str["access_token"][0]}
        if "expires" in query_str:
            result["expires"] = query_str["expires"][0]
        return result
    else:
        response = json.loads(content)
        raise GraphAPIError(response)


def get_app_access_token(app_id, app_secret):
    """Get the access_token for the app.

    This token can be used for insights and creating test users.

    app_id = retrieved from the developer page
    app_secret = retrieved from the developer page

    Returns the application access_token.

    """
    # Get an app access token
    args = {'grant_type': 'client_credentials',
            'client_id': app_id,
            'client_secret': app_secret}

    url = URL("https://graph.facebook.com/oauth/access_token")
    url.query.update(args)
    http = HTTPClient.from_url(url)
    resp = http.get(url.request_uri)
    content = resp.read()
    query_str = parse_qs(content)

    return query_str['access_token']


def get_app(access_token):
    """
        Get the app info from the access token

        access_token = retrieved from the user
    """
    http = GraphAPI(access_token)
    resp = http.request(path='/app')
    return resp


def send_notification(access_token, fb_id, template, href, ref):
    """
        Send a new Games Notification
        https://developers.facebook.com/docs/games/notifications/

            :param access_token: App access token
            :param fb_id: FB user id
            :param template: Message to send
            :param href: relative path of the target (using GET params)
                for example, index.html?gift_id=123
            :param ref: used to separate notifications into groups

            :returns: if success return a dict
                {'success': True}
            :raises: :class:`GraphAPIError`
    """
    path = URL('/{0}/notifications'.format(fb_id))
    post_args = {
        'template': template,
        'href': href,
        'ref': ref,
        'access_token': access_token}
    http = HTTPClient.from_url(FACEBOOK_URL)
    try:
        resp = http.post(path.request_uri, body=urlencode(post_args))
        content = _parse_json(resp.read())
    except Exception as e:
        raise GraphAPIError(e)
    finally:
        http.close()
    if content and isinstance(content, dict) and content.get('error'):
        raise GraphAPIError(content['error'])
    return content


