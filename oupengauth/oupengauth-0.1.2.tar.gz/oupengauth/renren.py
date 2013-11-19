from oauth import Oauth,oauth_call
import unittest
import time
import hashlib
import json
from datetime import datetime



class Renren(Oauth):
    api_url = "http://api.renren.com/restserver.do"
    auth_uri="https://graph.renren.com/oauth/authorize"
    token_uri="https://graph.renren.com/oauth/token"
    refresh_token = None
    user_nick = None
    oauth_type = "renren"

    @classmethod
    def hash_params(cls, params, app_secret):
        hasher = hashlib.md5("".join(["%s=%s" % (cls.unicode_encode(x), cls.unicode_encode(params[x])) for x in sorted(params.keys())]))
        hasher.update(app_secret)
        return hasher.hexdigest()

    @classmethod
    def unicode_encode(cls, str):
        return isinstance(str, unicode) and str.encode('utf-8') or str



    def get_access_token(self,code):
        data = json.loads(self._get_access_token(code))

        if data.has_key("error"):
            error_description = data.get("error_description",None)
            raise Exception(error_description)


        self.access_token = data.get('access_token',None)
        self.uid = data['user']['id']
        expires_in = data.get('expires_in',None)
        if expires_in:
            timestamp = time.time()+expires_in
            self.expired_at = datetime.fromtimestamp(timestamp)
        self.user_nick = data['user']['name']
        self.refresh_token = data.get('refresh_token',None)
        return data

    @oauth_call
    def users_getevent(self):
        params = {
            "method":"users.getEvent",
            "access_token":self.access_token,
            'call_id': str(int(time.time()*1000)),
            'v': '1.0',
            'format': 'json',
            'fields': 'friend_request_count,notification_count,new_message_count,fangle_count',
            "fangle_types":"100,110,120,130,140"
        }
        params['sig'] = Renren.hash_params(params, self.app_secret)
        return {
            "url":self.api_url,
            "method":"POST",
            "params":params
        }

    @oauth_call
    def token_refresh(self):
        params = {
            "grant_type":"refresh_token",
            "refresh_token":self.refresh_token,
            "client_id":self.app_key,
            "client_secret":self.app_secret
        }
        return {
            "url":self.token_uri,
            "method":"POST",
            "params":params
        }


        


