#coding:utf8
from oauth import Oauth,oauth_call
import unittest
import json,time
from datetime import datetime
import requests
from pyquery import PyQuery as pq
import urlparse
import time



class Sina(Oauth):
    auth_uri="https://api.weibo.com/oauth2/authorize"
    token_uri="https://api.weibo.com/oauth2/access_token"
    oauth_type = "sina"

    def get_access_token(self,code):
        data = json.loads(self._get_access_token(code))

        if data.has_key("error"):
            error_description = data.get("error_description",None)
            raise Exception(error_description)
       

        self.access_token = data.get('access_token',None)
        self.uid = data['uid']
        expires_in = data.get('expires_in',None)
        if expires_in:
            timestamp = time.time()+expires_in
            self.expired_at = datetime.fromtimestamp(timestamp)
        self.refresh_token = data.get('refresh_token',None)
        return data
    
    @oauth_call
    def user_show(self):
        return {
            "url":"https://api.weibo.com/2/users/show.json",
            "method":"GET",
            "params":{
                "access_token":self.access_token,
                "uid":self.uid,
            }
        }

    @oauth_call
    def account_get_uid(self):
        return {
            "url":"https://api.weibo.com/2/account/get_uid.json",
            "method":"GET",
            "params":{
                "access_token":self.access_token,
            }
        }
        
    def exchange_token(self,username,password):
        url = self.get_auth_uri()
        r = requests.get(url)
        d = pq(r.text)
        display =  d.items("input[@name=display]").next().val()
        response_type = d.items("input[@name=response_type]").next().val()
        regCallback = d.items("input[@name=regCallback]").next().val()
        redirect_uri = d.items("input[@name=redirect_uri]").next().val()
        client_id = d.items("input[@name=client_id]").next().val()
        state  = d.items("input[@name=state]").next().val()
        
        if (display is None and response_type is None):
            raise Exception("weibo auth error")
            
        
        payload = {
            "display":display,
            "response_type":response_type,
            "regCallback":regCallback,
            "redirect_uri":redirect_uri,
            "client_id":client_id,
            "state":state,
            "userId":username,
            "passwd":password,
            "action":"submit"
        }
        
        headers = {
            "Referer":url,
        }
        
        r = requests.post(self.auth_uri,data=payload,headers=headers, allow_redirects=False)
        location = r.headers['location']
        parser = urlparse.urlparse(location)
        params = urlparse.parse_qs(parser.query)
        code = params['code']
        return self.get_access_token(code[0])
        
        
        
        




        



