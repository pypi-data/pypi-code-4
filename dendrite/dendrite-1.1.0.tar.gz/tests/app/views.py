from dendrite.views import OAuth1Mixin, OAuth1ConnectView, OAuth1CallbackView
from .models import TwitterProfile

import json, requests, os 

class TwitterMixin(OAuth1Mixin):
    client_id         = os.environ.get('TWITTER_CLIENT_ID', '')
    client_secret     = os.environ.get('TWITTER_CLIENT_SECRET', '')
    request_token_url = 'https://api.twitter.com/oauth/request_token'
    authorization_url = 'https://api.twitter.com/oauth/authorize'
    access_token_url  = 'https://api.twitter.com/oauth/access_token'

    profile_class = TwitterProfile

class TwitterConnectView(TwitterMixin, OAuth1ConnectView):
    pass

class TwitterCallbackView(TwitterMixin, OAuth1CallbackView):
    def get_remote_profile(self, request, token):
        data = json.loads(
            requests.get('https://api.twitter.com/1.1/account/verify_credentials.json', params={
                    'skip_status': True, 'include_entities': False},
                         auth=self.client.auth).content)

        return dict([(f.name, data[f.name]) for f in self.profile_class._meta.fields if f.name in data])


