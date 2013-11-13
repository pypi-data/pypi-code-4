from flask_oauth import OAuth
from flask_heroku_auth import utils
from flask import request, redirect, abort, url_for, session
import functools
import requests


class CurrentUser(object):
    logged_in = utils.SessionDescriptor('heroku_auth_logged_in')
    username = utils.SessionDescriptor('heroku_auth_username')
    id = utils.SessionDescriptor('heroku_auth_id')
    token = utils.SessionDescriptor('heroku_auth_token')
    next_endpoint = utils.SessionDescriptor('heroku_auth_next_endpoint')
    next_url = utils.SessionDescriptor('heroku_auth_next_url')
    expires_in = utils.SessionDescriptor('heroku_auth_expires_in', 0)
    expiry_time = utils.SessionDescriptor('heroku_auth_expiry_time', 0)
    refresh_token = utils.SessionDescriptor('heroku_auth_refresh_token')

    @property
    def valid(self):
        if not self.logged_in:
            return True
        # Randomly check and refresh
        if self.expiry_time < utils.utc_timestamp():
            return False
        if self.expires_in <= 0:
            return False
        return True

    def reset(self):
        self.logged_in = False
        self.username = None
        self.id = None
        self.token = None

    @property
    def client(self):
        headers = {
            'Authorization': 'Bearer %s' % self.token,
            'Accept': 'application/vnd.heroku+json; version=3'
        }
        r = requests.session()
        r.trust_env = False
        r.headers.update(headers)
        return utils.URLPatch(r)

    def impersonate(self, user=None):
        r = requests.Session()
        #r.request = utils.PatchedSession.request
        r.trust_env = False
        r.headers.update(**{
            'Authorization': 'Bearer %s' % self.token,
            'Accept': 'application/vnd.heroku+json; version=3',
            "X-Heroku-Sudo": "true",
        })
        if user:
            r.headers.update(**{
                "X-Heroku-Sudo-User": user
            })
        return utils.URLPatch(r)

    def __repr__(self):
        return "<User %s>" % self.username

class HerokuOAuth(object):

    scope = property(lambda x: x.app.config.get('HEROKU_OAUTH_SCOPE'))
    auth_path = property(lambda x: x.app.config.get('HEROKU_OAUTH_PATH'))
    id = property(lambda x: x.app.config.get('HEROKU_OAUTH_ID'))
    secret = property(lambda x: x.app.config.get('HEROKU_OAUTH_SECRET'))
    baseurl = property(lambda x: x.app.config.get('HEROKU_OAUTH_BASE_URL'))
    logout_path = property(lambda x: x.app.config.get('HEROKU_OAUTH_LOGOUT_PATH'))
    scope = property(lambda x: x.app.config.get('HEROKU_OAUTH_SCOPE'))
    current = CurrentUser()

    def __init__(self, app):

        app.config.setdefault('HEROKU_OAUTH_SCOPE', 'global')
        app.config.setdefault('HEROKU_OAUTH_PATH', '/auth/heroku/callback')
        app.config.setdefault('HEROKU_OAUTH_LOGOUT_PATH', '/auth/heroku/logout')
        app.config.setdefault('HEROKU_OAUTH_BASE_URL', 'http://localhost:5000/')
        app.config.setdefault('HEROKU_OAUTH_ID', None)
        app.config.setdefault('HEROKU_OAUTH_SECRET', None)

        self.app = app

        oauth = OAuth()
        self.oauth = oauth.remote_app('heroku',
            base_url=self.baseurl,
            request_token_url=None,
            access_token_url='https://id.heroku.com/oauth/token',
            authorize_url='https://id.heroku.com/oauth/authorize',
            consumer_key=self.id,
            consumer_secret=self.secret,
            request_token_params={
                'response_type': 'code',
                'scope': self.scope
            }
        )

        self.app.add_url_rule(
            self.auth_path,
            view_func=self.authorize,
            endpoint="heroku_auth_login"
        )

        self.app.add_url_rule(
            self.logout_path,
            view_func=self.logout,
            endpoint="heroku_auth_logout"
        )

    def login(self):

        def auth():
            self.current.next_endpoint = request.endpoint
            self.current.next_url = request.url or "/"
            return self.oauth.authorize(callback=url_for('heroku_auth_login'))

        if request.endpoint in ([
            "heroku_auth_login",
            "heroku_auth_logout",
            "heroku_auth_redirect",
            None
            ]):
            return None

        if not self.current.valid:
            return auth()

        f = self.app.view_functions.get(request.endpoint)

        if self.current.logged_in:
            if getattr(f, '_herokai_only', False) and not utils.is_herokai(self.current.username):
                abort(401)
            return None

        return auth()

    def authorize(self):
        code = request.args.get('code')
        if not code:
            abort(403)

        d = self.exchange_code_to_token(code)

        token = d.get('access_token')
        refresh_token = d.get('refresh_token')
        expires_in = d.get('expires_in')

        user = self.load_user(token)

        email = user.get('email')
        id = user.get('id')

        f = self.app.view_functions.get(self.current.next_endpoint)

        if getattr(f, '_herokai_only', False) and not utils.is_herokai(email):
            abort(401)

        self.current.logged_in = True
        self.current.token = token
        self.current.id = id
        self.current.username = email
        self.current.refresh_token = refresh_token
        self.current.expires_in = expires_in
        self.current.expiry_time = utils.utc_timestamp() + expires_in

        return redirect(self.current.next_url)

    def logout(self):
        self.current.reset()
        session.clear()
        return redirect('https://id.heroku.com/logout')

    def exchange_code_to_token(self, code):
        d = {
            "grant_type": "authorization_code",
            "code": code,
            "client_secret": self.secret
        }
        r = requests.session()
        r.trust_env = False
        resp = r.post('https://id.heroku.com/oauth/token', data=d)
        if resp.status_code != 200:
            abort(resp.status_code)
        return resp.json()

    def load_user(self, code):
        """
        Helper method to obtain the username of the logged-in user.
        """

        headers = {
            'Authorization': 'Bearer %s' % code,
            'Accept': 'application/vnd.heroku+json; version=3'
        }
        r = requests.session()
        r.trust_env = False
        resp = r.get('https://api.heroku.com/account', headers=headers)
        return resp.json()
