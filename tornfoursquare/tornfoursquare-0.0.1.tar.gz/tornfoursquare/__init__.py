import urllib
import logging
import datetime
from tornado import httpclient
from tornado.httputil import url_concat
import tornado.escape


class FoursquareMixin:
    """Foursquare Oauth2 authentication.
    """
    
    _OAUTH_ACCESS_TOKEN_URL = "https://foursquare.com/oauth2/access_token"
    _OAUTH_AUTHORIZE_URL = "https://foursquare.com/oauth2/authorize"
    _OAUTH_AUTHENTICATE_URL = "https://foursquare.com/oauth2/authenticate"
    
    def _oauth_customer_token(self):
        self.require_setting("FOURSQUARE_CUSTOMER_KEY", "Foursquare OAuth")
        self.require_setting("FOURSQUARE_CUSTOMER_SECRET", "Foursquare OAuth")
        return dict(
            client_id = self.settings["FOURSQUARE_CUSTOMER_KEY"],
            client_secret = self.settings["FOURSQUARE_CUSTOMER_SECRET"])
    
    def authenticate_redirect(self):
        self.redirect(url_concat(self._OAUTH_AUTHENTICATE_URL, dict(
            redirect_uri = self.get_uri(),
            response_type = 'code',
            client_id = self._oauth_customer_token()["client_id"])))
    
    def get_authenticated_user(self, callback):
        kwargs = dict(
            code = self.get_argument('code'),
            redirect_uri = self.get_uri(),
            grant_type = 'authorization_code')
        kwargs.update(self._oauth_customer_token())
        http = httpclient.AsyncHTTPClient()
        http.fetch(url_concat(self._OAUTH_ACCESS_TOKEN_URL, kwargs),
            self.async_callback(self._on_access_token, callback))

    def _on_access_token(self, callback, response):
        if response.error:
            logging.warning("Could not fetch access token in Foursquare OAuth")
            callback(None)
            return
        
        session = tornado.escape.json_decode(response.body)
        self.foursquare_request(
            path="/users/self",
            callback=self.async_callback(self._parse_user_response, callback, session),
            access_token=session["access_token"])

    def _parse_user_response(self, callback, session, user):
        if user is None:
            callback(None)
            return
        user.update(dict(access_token = session['access_token']))
        callback(user)
    
    def foursquare_request(self, path, callback=None, access_token=None, post_args=None, **args):
        if path.startswith('http:') or path.startswith('https:'):
            url = path
        else:           
            url = "https://api.foursquare.com/v2" + path
        args.update(dict(v=datetime.datetime.now().strftime('%Y%m%d')))
        all_args = dict()
        all_args.update(args)
        all_args.update(post_args or {})
        
        if access_token is True:
            #
            # https://developer.foursquare.com/overview/auth#userless
            #
            all_args.update(self._oauth_customer_token())
        elif access_token:
            all_args["oauth_token"] = access_token
        elif access_token is False:
            raise tornado.web.HTTPError(500, "Must be logged in to use this feature.")

        if args:
            url += "?" + urllib.urlencode(all_args)

        callback = self.async_callback(self._on_foursquare_request, callback)
        http = httpclient.AsyncHTTPClient()
        if post_args is not None:
            http.fetch(url, method="POST", body=urllib.urlencode(all_args), callback=callback)
        else:
            http.fetch(url, callback=callback)

    def _on_foursquare_request(self, callback, response): 
        response_body = tornado.escape.json_encode(response.body)
        if response.error:
            logging.warning(
                "Foursquare Error(%s) :: Message: %s, URL: %s",
                response.error, response_body["meta"]["errorDetail"], response.request.url)
            callback(None)
            return
        callback(response_body)
