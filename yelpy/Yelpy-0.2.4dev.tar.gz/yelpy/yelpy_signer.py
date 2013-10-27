import oauth2
import os

class YelpySigner(object):

    def __init__(self, consumer_key=None, consumer_secret=None, token=None, token_secret=None):
        super(YelpySigner, self).__init__()
        self.consumer_key = consumer_key or os.environ['YELPY_CONSUMER_KEY']
        self.consumer_secret = consumer_secret or os.environ['YELPY_CONSUMER_SECRET']
        self.token = token or os.environ['YELPY_TOKEN']
        self.token_secret = token_secret or os.environ['YELPY_TOKEN_SECRET']

    def sign(self, url):
        consumer = oauth2.Consumer(self.consumer_key, self.consumer_secret)
        oauth_request = oauth2.Request('GET', url, {})
        oauth_request.update({
            'oauth_nonce': oauth2.generate_nonce(),
            'oauth_timestamp': oauth2.generate_timestamp(),
            'oauth_token': self.token,
            'oauth_consumer_key': self.consumer_key,
        })
        token = oauth2.Token(self.token, self.token_secret)
        oauth_request.sign_request(oauth2.SignatureMethod_HMAC_SHA1(), consumer, token)
        return oauth_request.to_url()
