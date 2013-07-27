# -*- coding: utf-8 -*-
""" This module makes signed requests of the HearPlanet API.

    Requests may be signed with an Application key, a User key,
    or both.

    USER_CREDENTIALS = {
            'name':u'myname',
            'key':u'C0ckK619NMaqm/n7ed4CLs747oi3qjxDCeRMkWyJxoQ='
    }
    APP_CREDENTIALS = {
            'name':u'myapplication',
            'key':u'8A5GyfmtLiDQR9C++Z/BXaoAIc5JkzWr+C65U0Iu+4w='
    }

    req = APIRequest('/api/2.0/article.json/search/',
        app_auth=APP_CREDENTIALS)
    resp = req.urlopen()
    json = resp.read()

    The signed request is passed on to urllib2.urlopen(), and the return
    value is a file-like object, as returned by urllib2.

    You can also just sign the url, and then open it some other way --
    keeping in mind that the signature will expire in TIMEWINDOW seconds.
    req = APIRequest('/api/2.0/article.json/search/', app_auth=APP_CREDENTIALS)
    url = req.sign()
    httplib2.Http().request(url)


"""
import datetime
import hashlib
import time
import urllib
import urllib2
import requests
import json
import logging as log
from query.table import Table
from urllib import urlencode

import check_version
import config

# URL expires after this many seconds
TIMEWINDOW = 60*5

log.basicConfig()
if config.LOG_LEVEL in log._levelNames:
    log.getLogger().setLevel(eval('log.%s' % config.LOG_LEVEL))


class HearPlanet(object):
    """ The HearPlanet Request object.
    """
    def __init__(self, app_auth={}, user_auth={}):
        """ The endpoint argument is required, and defines the API
            endpoint being accessed.  The data and headers variables
            are passed through to urllib2.urlopen().  With no data, the
            request will be a GET.  With data, the request method will
            be POST -- or PUT if the "method" variable is set to PUT.
            The app_auth and user_auth dictionaries contain a name and
            a key.  Finally, any other keyword args are added to the
            request as http vars.
        """
        if not app_auth: app_auth = config.APP_CREDENTIALS
        if not user_auth: user_auth = config.USER_CREDENTIALS
        self.api = API(app_auth, user_auth)


    def table(self, table):
        return Table(self.api, '%s.%s' % (table, config.EMITTER_FORMAT))

    def query(self, endpoint, data=None, headers={}, method=None, **kwargs):
        """ The endpoint argument is required, and defines the API
            endpoint being accessed.  The data and headers variables
            are passed through to urllib2.urlopen().  With no data, the
            request will be a GET.  With data, the request method will
            be POST -- or PUT if the "method" variable is set to PUT.
            The app_auth and user_auth dictionaries contain a name and
            a key.  Finally, any other keyword args are added to the
            request as http vars.
        """
        self.endpoint = endpoint
        self.data = data
        self.headers = headers
        self.method = method
        self.defaults = kwargs


class APIKey(object):
    """ Base class for AppKey and UserKey.  Don't use this directly, use
        AppKey() or UserKey(), or CombinedKey(AppKey(), UserKey()).
    """
    def __init__(self, keylabel, siglabel, classlabel, label, key, *args, **kwargs):
        self.keylabel = keylabel
        self.siglabel = siglabel
        self.classlabel = classlabel
        self.label = label
        self.key = key
        self.ignore = list(kwargs.pop('ignore',[]))
        self.ignore.append('csrfmiddlewaretoken')

    def __unicode__(self):
        return "%s for %s=%s" % (self.classlabel, self.label, self.key)

    def string_from_dict(self, workdict):
        """ Convert dictionary into UTF-8 encoded string.
        """
        keys = workdict.keys()
        keys.sort()
        work = []
        for key in keys:
            if not key in self.ignore:
                v = workdict[key]
                work.append(u'%s=%s' % (key, v))
        ret = u'\n'.join(work)
        ret = ret.encode('utf-8')
        return ret

    def _sanitize_dict(self, workdict):
        """ Convert all keys and values in dictionary to unicode, and removes
            any '\r' characters.
        """
        clean = {}
        for k, v in workdict.items():
            if type(k) is not unicode: k = unicode(k, 'utf-8')
            try:
                if type(v) is not unicode: v = unicode(v, 'utf-8')
            except TypeError:
                # values may be User or Application, and unicode() only
                # accepts str and buffer as arg, not objects
                v = unicode(str(v), 'utf-8')
            clean[k] = v.replace(u'\r', u'')
        return clean

    def _timestamp_now(self):
        timestamp = datetime.datetime.now()
        timestamp = time.mktime(timestamp.timetuple())
        return int(timestamp)

    def sign_dict(self, workdict):
        processor = hashlib.md5(self.key)
        timestamp = workdict.get('timestamp', None)
        if timestamp is not None:
            try:
                timestamp = int(timestamp)
            except (ValueError, TypeError):
                timestamp = None
        if timestamp is None:
            timestamp = self._timestamp_now()
            workdict['timestamp'] = unicode(timestamp)

        workdict = self._sanitize_dict(workdict)

        work = self.string_from_dict(workdict)
        processor.update(work)
        sig = processor.hexdigest()
        ret = workdict.copy()
        ret[self.keylabel] = self.label
        ret[self.siglabel] = sig
        return ret

    def sign(self, work):
        processor = hashlib.md5(self.key)
        processor.update(work)
        return processor.hexdigest()

    def verify_dict(self, workdict):
        """ Verify that the workdict was signed with the key.
        """
        ret = workdict.copy()
        ret = self._sanitize_dict(ret)

        # don't pop the keylabel, it should be included in what is signed
        api = ret.get(self.keylabel, None)
        if api is None:
            return (False, 'No %s' % self.classlabel)

        # at this point the api value (e.g. the user label) has already been
        # converted to unicode by sanitize_dict().  The self.label value is
        # already unicode, so we should be able to compare them directly.
        if api != self.label:
            return (False, '%s does not match' % self.classlabel)

        timestamp = ret.get('timestamp', None)
        if timestamp is None:
            return (False, 'No Timestamp')
        try:
            timestamp = int(timestamp)
        except (ValueError, TypeError):
            return (False, 'Could not parse timestamp: %s' % timestamp)

        if timestamp is None:
            return (False, 'No timestamp')

        sig = ret.pop(self.siglabel, None)
        if sig is None:
            return (False, "No Signature")

        work = self.string_from_dict(ret)
        result = self.verify(sig, timestamp, work)
        if not result[0]:
            pass

        return result

    def verify(self, signature, timestamp, workstring):
        now = self._timestamp_now()

        if abs(now - timestamp) > TIMEWINDOW:
            return (False, 'Timestamp expired')

        processor = hashlib.md5(self.key)
        processor.update(workstring)
        calculated = processor.hexdigest()

        if calculated.lower() == signature.lower():
            return (True,'OK')
        else:
            log.info('API Key verification failure: %s != %s', calculated, signature)

        return (False,'Signature not valid')

class UserKey(APIKey):
    """ UserKey class.
    """
    def __init__(self, *args, **kwargs):
        super(UserKey, self).__init__(
            'user', 'sig', 'UserKey', *args, ignore=('app','appsig'), **kwargs)

class AppKey(APIKey):
    """ AppKey class.
    """
    def __init__(self, *args, **kwargs):
        super(AppKey, self).__init__(
            'app', 'appsig', 'AppKey', *args, ignore=('user','sig'), **kwargs)

class CombinedKey:
    """ AppKey and UserKey combined.
    """
    ignore = ('sig', 'appsig')

    def __init__(self, appkey, userkey):
        self.appkey = appkey
        self.userkey = userkey

    def string_from_dict(self, workdict):
        """ Convert dictionary into string.
        """
        keys = workdict.keys()
        keys.sort()
        work = []
        for key in keys:
            if not key in self.ignore:
                v = workdict[key]
                work.append(u'%s=%s' % (key, v))
        ret = u'\n'.join(work)
        ret = ret.encode('utf-8')
        self.last_signed = ret
        return ret

    def sign_dict(self, workdict):
        """ Sign a dictionary with both user and app keys.
        """
        ret = {}
        userdict = workdict.copy()
        appdict = workdict.copy()

        userdict = self.userkey.sign_dict(userdict)
        appdict['timestamp'] = userdict['timestamp']
        appdict = self.appkey.sign_dict(appdict)

        ret.update(appdict)
        ret.update(userdict)

        return ret

    def sign(self, work):
        """ Sign request with CombinedKey.
            Returns (usersig, appsig) tuple.
        """
        usersig = self.userkey.sign(work)
        appsig = self.appkey.sign(work)
        return usersig, appsig

    def verify_dict(self, work):
        """ Verify signature.
            Returns (success/fail, message) tuple.
        """
        success, message = self.appkey.verify_dict(work)
        if success:
            success, message = self.userkey.verify_dict(work)

        return success, message

class API(object):
    def __init__(self, app_auth, user_auth, **kwargs):
        self.client = requests.session()
        self.app_auth = app_auth
        self.user_auth = user_auth
        self.defaults = kwargs
        # Get the key to use for signing.
        if self.app_auth and self.user_auth:
            self.key = CombinedKey(
                    AppKey(app_auth['name'], app_auth['key']),
                    UserKey(user_auth['name'], user_auth['key']))
        elif self.app_auth:
            self.key = AppKey(app_auth['name'], app_auth['key'])
        elif self.user_auth:
            self.key = UserKey(user_auth['name'], user_auth['key'])
        else:
            log.error('Need at least one of app or user to generate sig')
            raise ValueError('Need at least one of app or user to generate sig')

    def get(self, query):
        response = self._handle_request(query.path, query.params)
        return response

    def post(self, query):
        response = self._make_post_request(query.path, query.params)
        return response

    def schema(self, query):
        response = self._handle_request(query.path + '/schema', query.params)
        return response['view']

    def raw_read(self, path, raw_params):
        url = self._build_base_url(path)
        if isinstance(raw_params, str):
            url += raw_params
        else:
            url += self._make_query_string(raw_params)
        return self._make_request(url).text

    def build_url(self, path, params):
        #url = self._build_base_url(path) + self._make_query_string(params)
        url = self.sign(path, params)
        return url

    def _build_base_url(self, path):
        return 'http://' + config.HEARPLANET_HOST + config.BASE_URL + path + '/?'

    def _handle_request(self, path, params):
        url = self.build_url(path, params)
        response = self._make_request(url)
        if not 200 <= response.status_code < 300:
            raise APIException(response.status_code, response.text, url)
        if int(response.headers['content-length']) == 0:
            raise APIException(response.status_code, response.text, url)
        payload = json.loads(response.text)
        #if payload['status'] != 'ok':
            #raise APIException(response.status_code, payload, url)
        #return payload['response']
        return payload

    def _make_request(self, url):
        headers = {'X-HearPlanet-Lib': config.DRIVER_VERSION_TAG}
        response = self.client.get(url, headers=headers)
        return response

    def _make_post_request(self, path, params):
        url = self.build_url(path, params)
        headers = {'X-HearPlanet-Lib': config.DRIVER_VERSION_TAG}
        response = self.client.post(url, headers=headers)
        payload = json.loads(response.text)
        if payload['status'] != 'ok':
            raise APIException(response.status_code, payload, url)
        return payload['response'] if 'response' in payload else payload

    def _make_query_string(self, params):
        string_params = []
        for key, val in params.items():
            transformed = json.dumps(val) if not isinstance(val, str) else val
            string_params.append((key, transformed))
        return urlencode(string_params)

    def sign(self, path, params, **kwargs):
        """ Sign the request, and return the signed URL.
        """
        work = self.defaults.copy()
        work['url'] = config.BASE_URL + path + '/'
        work.update(params)
        work.update(kwargs)
        if self.app_auth: work['app'] = self.app_auth['name']
        if self.user_auth: work['user'] = self.user_auth['name']

        #if self.data: work['raw_data'] = self.data

        # Encrypt and encode the password; must come after getting the appkey.
        # Note that this is a special case when accessing the auth endpoint.
        # Also, if sending a password in JSON to user endpoint (when creating a
        # new user), the password in the data must also be encoded.  However,
        # that is not handled here.
        #if 'password' in work:
            #work['password'] = hp_encrypt(self.appkey, work['password'], 'aes')

        # Now do the signing.
        signed = self.key.sign_dict(work)

        # Verify 
        #self.key.verify_dict(signed)

        # The signstring that's displayed contains the raw data.
        # This is just so we can display what actually got signed.
        cleansigned = signed.copy()
        for k in ('appsig', 'sig',):
            if k in cleansigned:
                del cleansigned[k]
        signstring = self.key.string_from_dict(cleansigned)

        # The url should not contain the raw POST data, so remove it.
        if signed.has_key('raw_data'):
            del signed['raw_data']
        url = signed.pop('url')

        # Must encode the unicode values in dictionary for urlencode()
        for k,v in signed.items():
            signed[k] = v.encode('utf-8')

        url = u'%s?%s' % (url, urllib.urlencode(signed))

        self.url = "http://%s:%d%s" % (config.HEARPLANET_HOST, config.HEARPLANET_PORT, url)

        return self.url

class APIException(Exception):
    def __init__(self, status_code, response, url):
        self.status_code = status_code
        self.response = response
        self.url = url
        exception = {'http_status_code':status_code,'response':response, 'url':url}
        Exception.__init__(self, exception)

    def get_status_code(self):
        return self.status_code

    def get_response(self):
        return self.response
