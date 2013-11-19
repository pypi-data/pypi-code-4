from oauth import Oauth,oauth_call
import unittest
import urllib
import time
import base64
import json


from datetime import datetime


class QQ(Oauth):
    oauth_type = "qq"
    auth_uri="https://open.t.qq.com/cgi-bin/oauth2/authorize"
    token_uri="https://open.t.qq.com/cgi-bin/oauth2/access_token"

    user_nick = None
    public_params = None

    def get_auth_uri(self):
        params = {
            "client_id":self.app_key,
            "redirect_uri":self.redirect_uri,
            "response_type":"code",
            "wap":"2",
        }
        url = "%s?%s" % (self.auth_uri,urllib.urlencode(params))
        return url



    def get_access_token(self,code,openid):
        content = self._get_access_token(code)
        data = {}
        rows = content.split('&')
        for row in rows:
            key,value = row.split("=")
            data[key]=value

        if data.has_key("error"):
            error_description = data.get("error_description",None)
            raise Exception(error_description)

        self.access_token = data.get('access_token',None)
        self.uid = openid
        expires_in = data.get('expires_in',None)
        if expires_in:
            timestamp = time.time()+int(expires_in)
            self.expired_at = datetime.fromtimestamp(timestamp)
        self.user_nick = data.get("name")

        self.public_params = {
            "oauth_consumer_key":str(self.app_key),
            "access_token":self.access_token,
            "openid":self.uid,
            "clientip":"127.0.0.1",
            "oauth_version":"2.a",
            "scope":"all",
        }

        return data

    @oauth_call
    def info_update(self,op=0,optype=0):
        params = {
            "format":"json",
            "op":op,
            "type":optype,
        }
        params.update(self.public_params)
        return {
            "url":"https://open.t.qq.com/api/info/update",
            "method":"GET",
            "params":params
        }
    

