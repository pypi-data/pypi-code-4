"""WSGI Middleware for catching exceptions and sending to TaskWorkshop."""

from .client import Client
from .utils import get_environ_dict


class TaskWorkshopMiddleware(object):

    """A WSGI middleware for catching exceptions and sending to TaskWorkshop.

    Each exception raised by application is catched and sent to specified
    TaskWorkshop URL as an exception event.

    Usage::

        >>> from twlogger.middleware import TaskWorkshopMiddleware
        >>> from myproject import wsgi_app
        >>> error_catching_wsgi_app = TaskWorkshopMiddleware(wsgi_app)

    Or in a PasteDeploy pipeline::

        [filter:twlogger]
        use = egg:TWLogger#twlogger
        url = https://taskworkshop.com/exceptions/log/YOUR_TOKEN

        [pipeline:main]
        pipeline =
            twlogger
            your-app

        [app:your-app]
        ...

    :param app: WSGI application object
    :param url: TaskWorkshop exceptions log URL.  If none given, it will be
        read from ``TWLOGGER_URL`` environment variable.
    :param client: :class:`twlogger.client.Client` object, optional

    """

    def __init__(self, app, url=None, client=None):
        self.app = app
        self.client = client or Client(url)

    def __call__(self, environ, start_response):
        try:
            app_iter = self.app(environ, start_response)
        except Exception:
            self.handle_exception(environ)
            raise

        try:
            for event in app_iter:
                yield event
        except Exception:
            self.handle_exception(environ)
            raise
        finally:
            if (app_iter and
                    hasattr(app_iter, 'close') and
                    callable(app_iter.close)):
                try:
                    app_iter.close()
                except:
                    self.handle_exception(environ)
                    raise

    def handle_exception(self, environ):
        """Build environment dictionary, catch exception and send event.

        :param environ: request environment dictionary

        """
        environment = get_environ_dict(environ)
        self.client.capture_exception(**environment)


def make_middleware(app, global_conf, url=None, client=None):
    """Return given app wrapped in :class:`TaskWorkshopMiddleware`."""
    return TaskWorkshopMiddleware(app, url=url, client=client)
