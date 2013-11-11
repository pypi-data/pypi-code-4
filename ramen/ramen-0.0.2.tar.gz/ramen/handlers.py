from tornado import web, gen
from tornado.escape import parse_qs_bytes

from .views import JScriptView, HtmlView, JsonView

class Behavior:
    def __init__(self, handler, *args, **kwargs):
        self.handler = handler
        self.args = args
        self.kwargs = kwargs

    def respond(self):
        pass


class Redirect(Behavior):
    def respond(self):
        self.handler.redirect(self.kwargs.get('url'))


class Error(Behavior):
    def respond(self):
        self.handler.send_error(self.kwargs.get('code'))


class Handler(web.RequestHandler):
    http_get_view_adapter = None
    http_post_view_adapter = None

    def context(self):
        return {}

    def initialize(self, *args, **kwargs):
        self.install_translator()

    def install_translator(self):
        self.translator = self.application.translators.get(self.get_user_locale(), object())

    def _(self, message):
        return getattr(self.translator, 'ugettext', lambda x: x)(message)

    def _parse_arguments(self, src):
        arguments = {}
        for key, value in parse_qs_bytes(src, keep_blank_values=True).items():

            value = [x.decode('utf-8') for x in value]

            v = value
            if key.endswith('[]'):
                key = key[:-2]
            else:
                v = value[0]
            td = arguments
            parts = key.split('[')
            for i, tkey in enumerate(parts):
                tkey = tkey.strip('[]')
                if i+1 < len(parts):
                    td = td.setdefault(tkey, {})
            try:
                td[key.split('[')[-1].strip('[]')] = v
            except:
                pass

        return arguments

    @property
    def arguments(self):
        if not hasattr(self, '_parsed_arguments'):
            self._parsed_arguments = self._parse_arguments(self.request.query)

            if self.request.method == 'POST':
                self._parsed_arguments.update(self._parse_arguments(self.request.body))

        return self._parsed_arguments

    def send_response(self, v):
        for hname, hvalue in v.headers.iteritems():
            self.set_header(hname, hvalue)
        self.write(v.render())

    def complete(self, data):
        if isinstance(data, Behavior):
            data.respond()
        else:
            view = self.http_view_adapter(self, self.context, data) if self.http_view_adapter else self.view_factory(self.context, data)
            self.send_response(view)

        self.finish()

    @web.asynchronous
    @gen.coroutine
    @web.addslash
    def get(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

        self.context = yield self.get_context()
        can = yield self.can_get()

        if isinstance(can, Behavior):
            can.respond()
        elif not can:
            self.send_error(403)
        else:
            self.http_view_adapter = self.http_get_view_adapter
            __dummy = yield self.do_get()

    @web.asynchronous
    @gen.coroutine
    def post(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

        self.context = yield self.get_context()
        can = yield self.can_post()

        if isinstance(can, Behavior):
            can.respond()
        elif not can:
            self.send_error(403)
        else:
            self.http_view_adapter = self.http_post_view_adapter
            __dummy = yield self.do_post(context)


    def do_get(self):
        return {}

    def can_get(self):
        return True

    def do_post(self):
        return {}

    def can_post(self):
        return True

    def __init__(self, *args, **kwargs):
        super(Handler, self).__init__(*args, **kwargs)

        self.get_context  = self.application.asynchronize(self.get_context)

        self.can_get  = self.application.asynchronize(self.can_get)
        self.can_post = self.application.asynchronize(self.can_post)

        self.do_get   = gen.coroutine(self.do_get)
        self.do_post  = gen.coroutine(self.do_post)

        self.initkw = kwargs

    def view_factory(self, context, data):
        accept = self.request.headers.get('Accept', 'text/html')

        if 'application/javascript' in accept:
            return JScriptView(self, context, data)
        if 'application/json' in accept:
            return JsonView(self, context, data)
        else:
            return HtmlView(self, context, data)

