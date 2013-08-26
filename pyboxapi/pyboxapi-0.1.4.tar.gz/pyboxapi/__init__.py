import base64
import urllib
from urllib2 import HTTPError
from urlparse import urlparse, parse_qs

import json
import requests
import logging
import sys
import mechanize




"""
Steps to use this API:

1. Register an application at https://app.box.com/developers/services/edit/
2. Copy from the application page your client_id and client_secret.

Note that this API requires your box.com e-mail and password.
The reason for this is because the access_token is only valid for 1 hour
and can only be refreshed up to 14 days. This is an issue if you want to
create a program that needs permanent access to a Box.com account.

I wish Box.com would make the access_token or the refresh_token infinite.

boxapi.call('/folders','post', create_folder_item

"""

log = logging.getLogger(__name__)

class BoxApiException(Exception):
    pass

class BoxApi(object):

    BASE_URL = "https://api.box.com/2.0"
    UPLOAD_URL = "https://upload.box.com/api/2.0"

    BOX_API_RESOURCES = {
        'folders' : '/folders',
        'folders_items' : '/folders/%(folder_id)s/items',
        'folders_collaborations' : '/folders/%(folder_id)s/collaborations',
        'files' : '/files',
        'file_content' : '/files/content',
        'files_content' : '/files/%(file_id)s/content',
        'files_versions' : '/files/%(file_id)s/versions',
        'shared_items' : '/shared_items',
        'comments' : '/comments',
        'collaborations' : '/collaborations',
        'search' : '/search',
        'events' : '/events',
        'users' : '/users',
        'tokens' : '/tokens'
    }

    REST_METHOD_MAPPING = {
        'get' : 'get',
        'create' : 'post',
        'update' : 'put',
        'delete' : 'delete'
    }

    def __init__(self, client_id=None, client_secret=None):
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s', stream=sys.stdout)
        log.debug("Initializing BoxAPI class.")

        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None

    def obtain_access_token(self, username=None, password=None):
        mech = mechanize.Browser(factory=mechanize.DefaultFactory(i_want_broken_xhtml_support=True))
        mech.set_handle_robots(False)
        mech.set_debug_http(False)
        mech.addheaders = [('User-agent', 'User-Agent=Mozilla/5.0 (Windows NT 6.1; WOW64; rv:15.0) Gecko/20100101 Firefox/15.0')]

        try:
          url = "https://app.box.com/api/oauth2/authorize?response_type=code&client_id=%s" % self.client_id
          log.debug("Opening URL %s" % url)
          response = mech.open(url)
        except HTTPError, e:
          sys.exit("%d: %s" % (e.code, e.msg))

        # Select the form, fill the fields, and submit
        mech.select_form(nr=0)
        mech["login"] = username
        mech["password"] = password
        try:
          response = mech.submit()
        except HTTPError, e:
          sys.exit("Login into Box.com failed: %d: %s" % (e.code, e.msg))

        mech.select_form(nr=0)
        try:
          response = mech.submit()
        except HTTPError, e:
          sys.exit("Accept Failed: %d: %s" % (e.code, e.msg))

        o = urlparse(mech.geturl())
        code = parse_qs(o.query)['code'][0]

        headers = {'content-type': 'application/x-www-form-urlencoded'}
        data = {
          'grant_type' : 'authorization_code',
          'code' : code,
          'client_id' : self.client_id,
          'client_secret' : self.client_secret        
        }
        r = requests.post('https://www.box.com/api/oauth2/token', headers=headers, data=data)
        access_token = json.loads(r.text)['access_token']        
        self.access_token = access_token
        return access_token

    def set_access_token(self, token):
        self.access_token = token

    def verify_access_token(self):
        if self.access_token == None:
            return False
        return True

    """
    def get_folders
    def create_folders
        update_folder_items
        delete_folder_collaborations
        get_files

    """

    # Dynamically create the API call by intercepting method calls
    def __getattribute__(self, name):

        # Try to get the natural attribute off this object first
        try:
            attr = object.__getattribute__(self, name)
            return attr
        except AttributeError, e:
            pass

        # Since the attribute did not exist we create a method
        # based on the name of the attribute

        api_method_name = name
        rest_method, separator, rest_resource = api_method_name.partition("_")

        def api_method(*args, **kwargs):
            headers = {
                'Authorization' : 'Bearer %s' % self.access_token
            }

            http_method = self.REST_METHOD_MAPPING[rest_method]
            http_request_call = getattr(requests, http_method)


            if rest_resource in ['files','files_content'] and rest_method == 'create':
                print "Changing base url"
                url = self.UPLOAD_URL + self.BOX_API_RESOURCES[rest_resource]
            else:
                url = self.BASE_URL + self.BOX_API_RESOURCES[rest_resource]
            url = url % kwargs



            print kwargs.get('files',None)

            r = http_request_call(url, headers=headers, data=kwargs, files=kwargs.get('files',None))
            return json.loads(r.text)


        return api_method

