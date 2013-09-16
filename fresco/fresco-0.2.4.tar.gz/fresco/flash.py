from functools import partial
from urllib import quote_plus, unquote_plus

from fresco import context
from fresco import core

class FlashMiddleware(object):
    """
    Middleware to facilitate setting and displaying messages to the user across
    an http redirect.

    Usage::

        from fresco import flash

        def app1(request):
            flash.info("Operation completed")
            flash.warn("1 warning encountered")
            return Response.redirect('/app2.html')

        app1 = FlashMiddleware(app1)

        def app2(request):
            return Response("<p>Message was: %s</p>" % request.environ['fresco.flash_messages'])

    """

    INFO = 'INFO'
    WARN = 'WARN'
    ERROR = 'ERROR'

    __name__ = "FlashMiddleware"

    def __init__(self, app):
        self.app = app

    def _flash(self, messages, message, category=INFO):
        messages.append((category, message))

    def _start_response(self, environ, start_response, status, headers, exc_info=None):
        messages = environ['fresco.flash_messages']
        script_name = environ.get('SCRIPT_NAME', '') or '/'

        # Redirect response: set flash cookie so the messages are persisted to the next request
        if status[:2] == '30' and messages:
            cookies = [(
                'Set-Cookie',
                'fresco.flash=%s;path=%s' % (
                    ','.join(('%s:%s' % (c, m)).encode("base64") for c, m in messages).strip().replace('\n',''),
                    script_name,
                )
            )]
        elif 'fresco.flash' in environ.get('HTTP_COOKIE', ''):
            cookies = [('Set-Cookie', 'fresco.flash=;Expires=Tue, 01 Jan 1980 00:00:00;Path=' + script_name)]
        else:
            cookies = []

        headers.extend(cookies)
        return start_response(status, headers, exc_info)

    def __call__(self, environ, start_response):
        request = core.request_class(environ)
        flash_in = request.cookies.get('fresco.flash', None)
        if flash_in and flash_in.value:
            messages = [item.decode('base64').split(':', 1) for item in flash_in.value.split(',')]
        else:
            messages = []
        environ['fresco.flash_messages'] = messages
        environ['fresco.flash'] = partial(self._flash, messages)

        return self.app(environ, partial(self._start_response, environ, start_response))

def info(message):
    context.request.environ['fresco.flash'](message, FlashMiddleware.INFO)

def warn(message):
    context.request.environ['fresco.flash'](message, FlashMiddleware.WARN)

def error(message):
    context.request.environ['fresco.flash'](message, FlashMiddleware.ERROR)

def messages():
    """
    Return a list of (level, message) tuples flashed from the previous request
    """
    return context.request.environ['fresco.flash_messages']

