import functools
import requests
from flask_heroku_auth import utils
from flask import abort, g, request, current_app
import json


def build_client():
    headers = {
        'Accept': 'application/vnd.heroku+json; version=3'
    }
    r = requests.session()
    r.trust_env = False
    r.headers.update(headers)
    return utils.URLPatch(r)


class CurrentUser(object):

    @property
    def client(self):
        r = build_client()
        r.session.auth = (g._herokuauth_api_user, g._herokuauth_api_pass)
        return r

    @property
    def account(self):
        return g._herokuauth_api_account


class HerokuAPIAuth(object):

    def __init__(self, app):
        """

        """
        self.app = app

    @property
    def current(self):
        return CurrentUser()

    def authenticate(self, username, password):
        """

        """
        r = build_client()
        resp = r.get('/account', auth=(username, password))
        if resp.status_code != 200:
            current_app.logger.info(
                    'API Auth: Call to /account returned %s' % resp.status_code)
            current_app.logger.info(
                    'API Auth: %s' % json.dumps(resp.json()))
            abort(401)

        f = self.app.view_functions.get(request.endpoint)

        email = resp.json().get('email')

        if getattr(f, '_herokai_only', False) and not utils.is_herokai(email):
            current_app.logger.info(
                    'API Auth: Non-Herokai attempting to access Herokai Only')
            abort(401)

        g._herokuauth_api_user = username
        g._herokuauth_api_pass = password
        g._herokuauth_api_account = resp.json()
