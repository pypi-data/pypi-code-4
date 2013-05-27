from requests_oauthlib import OAuth1
import requests, json

class oauthnesia():
    api_base_url = "https://api1.urbanesia.com/"
    api_uri = ""

    consumer_key = ""
    consumer_secret = ""
    user_key = ""
    user_secret = ""

    def __init__(self, base_url=None, cons_key=None, cons_sec=None, user_key=None, user_sec=None):
        if base_url:
            self.api_base_url = base_url
        if cons_key:
            self.consumer_key = cons_key
        if cons_sec:
            self.consumer_secret = cons_sec
        if user_key:
            self.user_key = user_key
        if user_sec:
            self.user_secret = user_sec

    def call(self, uri, post=None, get=None, with_user_tokens=False, user_key=None, user_sec=None):
        self.api_uri = uri

        if with_user_tokens:
            if not user_key:
                raise Exception("Requesting an OAUTH resource with an empty user/token key")
            if not user_sec:
                raise Exception("Requesting an OAUTH resource with an empty user/token secret")

            self.user_key = user_key
            self.user_secret = user_sec

        url = "%s%s" % (self.api_base_url, uri)
        auth = self.get_auth(with_user_tokens=with_user_tokens)

        if post is None:
            response = requests.get(url, params=get, auth=auth)
        else:
            response = requests.post(url, params=get, data=post, auth=auth)

        try:
            return {
                'code': int(response.status_code),
                'data': json.loads(response.content)
            }
        except:
            print response.content
            return {
                'code': 500,
                'data': {'message':'Invalid HTTP Response'}
            }

    def xauth(self, username, password):
        self.api_uri = "oauth/access_token"

        url = "%s%s" % (self.api_base_url, self.api_uri)
        post = {
            'x_auth_username': username,
            'x_auth_password': password,
            'x_auth_mode': 'client_auth'
        }

        response = requests.post(url=url, data=post, auth=self.get_auth())

        try:
            return {
                'code': int(response.status_code),
                'data': json.loads(response.content)
            }
        except:
            print response.content
            return {
                'code': 500,
                'data': {'message':'Invalid HTTP Response'}
            }

    def get_auth(self, with_user_tokens=False):
        if not with_user_tokens:
            return OAuth1(self.consumer_key,
                          self.consumer_secret)
        else:
            return OAuth1(self.consumer_key,
                          self.consumer_secret,
                          self.user_key,
                          self.user_secret)