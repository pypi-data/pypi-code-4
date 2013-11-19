from oauth import Oauth,oauth_call
import unittest
from datetime import datetime
import json
import time
import urllib


class Taobao(Oauth):
    api_url = "https://eco.taobao.com/router/rest"
    auth_uri="https://oauth.taobao.com/authorize"
    token_uri="https://oauth.taobao.com/token"
    oauth_type = "taobao"
    taobao_user_nick = None

    def get_auth_uri(self):
        params = {
            "client_id":self.app_key,
            "redirect_uri":self.redirect_uri,
            "response_type":"code",
            "view":"wap",
        }
        url = "%s?%s" % (self.auth_uri,urllib.urlencode(params))
        return url
    
    @oauth_call
    def increment_customer_permit(self): 
        return {
            "url":self.api_url,
            "method":"GET",
            "params":{
                "method":"taobao.increment.customer.permit",
                "format":"json",
                "access_token":self.access_token,
                "v":"2.0",
            }
        }



    @oauth_call
    def user_get(self):
        return{
            "url":self.api_url,
            "method":"GET",
            "params":{
                "method":"taobao.user.get",
                "format":"json",
                "access_token":self.access_token,
                "v":"2.0",
                "fields":"nick"
            }
        }

    @oauth_call
    def increment_trades_get(self):
        return {
            "url":self.api_url,
            "method":"GET",
            "params":{
                "method":"taobao.increment.trades.get",
                "format":"json",
                "access_token":self.access_token,
                "v":"2.0"
            }
        }

    def get_access_token(self,code):
        data = json.loads(self._get_access_token(code))

        if data.has_key("error"):
            error_description = data.get("error_description",None)
            raise Exception(error_description)
        self.access_token = data.get('access_token',None)
        self.uid = data.get('taobao_user_id')
        expires_in = data.get('expires_in',None)
        if expires_in:
            timestamp = time.time()+int(expires_in)
            self.expired_at = datetime.fromtimestamp(timestamp)    
        self.user_nick = data['taobao_user_nick']

        return data



