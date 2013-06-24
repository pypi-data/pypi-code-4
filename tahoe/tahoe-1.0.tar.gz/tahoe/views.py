"""
The MIT License (MIT)

Copyright (c) 2013 Lunar Technology Corporation

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""
import urlparse
from functools import wraps
from werkzeug.local import LocalProxy
from flask import current_app, Response, request, _request_ctx_stack
from flask.ext.principal import Identity, identity_changed
from tahoe.encoding import json_dumps, json_handler


class ViewCollection(object):
    def __init__(self, prefix, app, version=1):
        if not prefix.endswith('/'):
            prefix += '/'
        self.prefix = prefix
        self.app = app
        self.version = version

    def add_route(self, relative_rule, **kwargs):
        def inner_function(view_function):
            use_prefix = kwargs.pop('use_prefix', True)
            use_version = kwargs.pop('use_version', True)

            if use_prefix:
                rule = urlparse.urljoin(self.prefix, relative_rule)
            else:
                rule = relative_rule

            if use_version:
                version_prefix = 'v{}/'.format(self.version)
                rule = urlparse.urljoin(version_prefix, rule)

            if not rule.startswith('/'):
                rule = '/' + rule

            self.app.add_url_rule(
                rule=rule,
                view_func=view_function,
                **kwargs)
        return inner_function


class ViewsRegistry(object):
    """
    A place to keep track of registered views and facilities to configure them
    and supplant them with application references.
    """
    view_callbacks = []

    def __init__(self, app, config, db, models, bucket, logger):
        self.db = db
        self.config = config
        self.app = app
        self.models = models
        self.bucket = bucket
        self.logger = logger

    @classmethod
    def register(cls, prefix='', version=1):
        """
        Registers a view and adds it to a list of views.  This defers the
        actualsetup of the views until we want to do it, and allows us to
        pass in important app objects that the views can use.
        """
        def inner(callback):
            options = dict(
                view_callback=callback,
                prefix=prefix,
                version=version)
            cls.view_callbacks.append(options)
        return inner

    def setup(self):
        """
        Takes the list of registered views and sets them up as the url rules
        that flask expects.

        Each view is wrapped in a closure that passes in applicaiton specific
        stuff that a view might need like a reference to the app object, the
        db, and the configuration.
        """
        for view_cb in self.view_callbacks:
            view_collection_callback = view_cb.get('view_callback')
            view_collection_prefix = view_cb.get('prefix')
            view_collection_version = view_cb.get('version')

            collection = ViewCollection(
                prefix=view_collection_prefix,
                app=self.app,
                version=view_collection_version)

            view_collection_callback(
                collection,
                db=self.db,
                app=self.app,
                config=self.config,
                models=self.models,
                bucket=self.bucket,
                logger=self.app.logger)

_security = LocalProxy(lambda: current_app.extensions['security'])

_default_unauthorized_html = """
    <h1>Unauthorized</h1>
    <p>The server could not verify that you are authorized to access the URL
    requested. You either supplied the wrong credentials (e.g. a bad
    password), or your browser doesn't understand how to supply the
    credentials required.</p>
    """


def _get_unauthorized_response(text=None, headers=None):
    text = text or _default_unauthorized_html
    headers = headers or {}
    return Response(text, 401, headers)


def _check_http_auth():
    if request.authorization:
        username = request.authorization.username
        password = request.authorization.password
        # Flask-Security provides something like this, but for some reason
        # looks up the user by their email (huh?) so I do it here by
        # username (Yuugh!), I also poke the authenticated user
        # into the request ctx so they appear as logged in via the
        # `current_user` proxy.
        user = _security.datastore.find_user(username=username)
        if user and user.verify_password(password):
            app = current_app._get_current_object()
            identity_changed.send(app, identity=Identity(user.id))
            ctx = _request_ctx_stack.top
            ctx.user = user
            return True
    return False


def http_auth_required(realm):
    """Decorator that protects endpoints using Basic HTTP authentication.
    The username should be set to the user's email address.

    :param realm: optional realm name"""

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if _check_http_auth():
                return fn(*args, **kwargs)
            r = _security.default_http_auth_realm if callable(realm) else realm
            h = {'WWW-Authenticate': 'Basic realm="%s"' % r}
            return _get_unauthorized_response(headers=h)
        return wrapper

    if callable(realm):
        return decorator(realm)
    return decorator


def json_response(output, status_code=200):
    if isinstance(output, basestring):
        output = dict(message=output)
    output = dict(r=output)
    response = (
        json_dumps(output, default=json_handler),
        status_code,
        {'Content-Type': 'application/json'}
        )
    return response


def paginate(query, page=None, per_page=None):
    """
    Paginates a passed in query object and returns the results.

    * By default this uses `page`=1 and the `per_page` amount set in the
      config.
    * If `page` or `per_page` are passed in via querystring, they will be
      used.
    * All of this can be overidden via the kwargs `page` and `per_page`
    """

    if not page:
        page = int(request.args.get('page', 1))

    if not per_page:
        default_per_page = 12  # TODO: pull from config
        per_page = int(request.args.get('per_page', default_per_page))

    if page < 1 or per_page < 1:
        return []

    return query.paginate(page, per_page=per_page, error_out=False).items
