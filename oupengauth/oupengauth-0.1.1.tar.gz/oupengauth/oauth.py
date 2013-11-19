import unittest
import urllib
import httplib2
import json
import time
from datetime import datetime
import base64

def oauth_call(func):

    def decorated(self,*args,**kwargs):
        oauth_data = func(self,*args,**kwargs)
        h = httplib2.Http(disable_ssl_certificate_validation=True)
        url = oauth_data['url']
        params = oauth_data['params']
        method = oauth_data['method']
        url = "%s?%s" % (url,urllib.urlencode(params))
        resp,content = h.request(url,method)
        return content

    return decorated

class Oauth(object):

    access_token = None
    expired_at =  None
    uid = None



    def __init__(self,app_key,app_secret,redirect_uri):
        self.app_key = str(app_key)
        self.app_secret = app_secret
        self.redirect_uri = redirect_uri


    def get_auth_uri(self):

        params = {
            "client_id":self.app_key,
            "redirect_uri":self.redirect_uri,
            "response_type":"code",
            "display":"wap2.0",
        }

        url = "%s?%s" % (self.auth_uri,urllib.urlencode(params))
        return url

    @oauth_call
    def _get_access_token(self,code):
        return {
            "url":self.token_uri,
            "method":"POST",
            "params":{
                "client_id":self.app_key,
                "client_secret":self.app_secret,
                "grant_type":"authorization_code",
                "code":code,
                "redirect_uri":self.redirect_uri,
            }
        }


    def get_access_token(self,code):
        data = json.loads(self._get_access_token(code))

        if data.has_key("error"):
            error_description = data.get("error_description",None)
            raise Exception(error_description)
        print data
        self.access_token = data.get('access_token',None)
        self.uid = data.get('uid',None)
        expires_in = data.get('expires_in',None)
        if expires_in:
            timestamp = time.time()+int(expires_in)
            self.expired_at = datetime.fromtimestamp(timestamp)

        return data








        
  
  


