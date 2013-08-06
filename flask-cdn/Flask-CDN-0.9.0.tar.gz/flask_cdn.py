from flask import url_for as flask_url_for
from flask import current_app


def url_for(endpoint, **values):
    """
    Generates a URL to the given endpoint.

    If the endpoint is for a static resource then a URL to the CDN is
    generated, otherwise the call is passed on to `flask.url_for`.

    Because this function is set as a jinja environment variable when
    `CDN.init_app` is invoked, this function replaces `flask.url_for` in
    templates automatically. It is unlikely that this function will need to be
    directly called from within your application code, unless you need to refer
    to static assets outside of your templates.
    """
    app = current_app

    if app.debug and not app.config['CDN_DEBUG']:
        return flask_url_for(endpoint, **values)

    if endpoint == 'static':
        scheme = 'http'

        if app.config['CDN_HTTPS']:
            scheme = 'https'

        urls = app.url_map.bind(app.config['CDN_DOMAIN'], url_scheme=scheme)

        return urls.build(endpoint, values=values, force_external=True)

    return flask_url_for(endpoint, **values)


class CDN(object):
    """
    The CDN object allows your application to use Flask-CDN.

    When initialising a CDN object you may optionally provide your
    :class:`flask.Flask` application object if it is ready. Otherwise,
    you may provide it later by using the :meth:`init_app` method.

    :param app: optional :class:`flask.Flask` application object
    :type app: :class:`flask.Flask` or None
    """
    def __init__(self, app=None):
        """
        An alternative way to pass your :class:`flask.Flask` application
        object to Flask-CDN. :meth:`init_app` also takes care of some
        default `settings`_.

        :param app: the :class:`flask.Flask` application object.
        """
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        defaults = [('CDN_DOMAIN', None),
                    ('CDN_DEBUG', False),
                    ('CDN_HTTPS', False)]

        for k, v in defaults:
            app.config.setdefault(k, v)

        if app.config['CDN_DOMAIN']:
            app.jinja_env.globals['url_for'] = url_for
