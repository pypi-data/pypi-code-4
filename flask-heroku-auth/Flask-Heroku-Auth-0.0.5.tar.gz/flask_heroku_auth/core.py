from flask_heroku_auth.oauth import HerokuOAuth
from flask_heroku_auth.api import HerokuAPIAuth
from flask_heroku_auth import utils
import functools
from flask import g, request, abort, current_app

class HerokuAuth(object):

    def __init__(self, app=None):

        if app:
            self.init_app(app)

    def init_app(self, app):

        self._oauth = HerokuOAuth(app)
        self._api = HerokuAPIAuth(app)
        
        @app.context_processor
        def inject_user():
            return dict(current_user=self.current)
            
        self.app = app

    herokai_only = utils.herokai_only

    @property
    def current(self):
        method = g.get('_heroku_auth_method')
        if not method:
            raise Exception('Current User requested outside Authorization Context')
        if method == "oauth":
            return self._oauth.current
        elif method == "api":
            return self._api.current
        else:
            raise Exception('Unknown Authorization Method')

    def oauth(self, f):
        """

        """
        @functools.wraps(f)
        def dec(*args, **kwargs):
            # Check auth hasn't been set before
            # Double check for not 2 mechanisms
            g._heroku_auth_method = "oauth"
            redirect = self._oauth.login()
            if redirect:
                return redirect
            return f(*args, **kwargs)
        return dec

    def api(self, f):
        """

        """
        @functools.wraps(f)
        def dec(*args, **kwargs):
            current_app.logger.info(
                    'API Authentication: Starting')
            g._heroku_auth_method = "api"
            if not request.authorization:
                current_app.logger.info(
                    'API Authentication Failed: Basic Auth not Provided')
                abort(401)
            u = request.authorization.get('username')
            p = request.authorization.get('password')
            self._api.authenticate(u, p)
            current_app.logger.info(
                    'API Authentication: Successful')
            return f(*args, **kwargs)
        return dec

    # Both Method
