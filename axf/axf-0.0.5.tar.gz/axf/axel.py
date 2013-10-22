import inspect
from tw2.core import core
from tw2.core import middleware
from tw2.core import js_function, Param, js_callback, Link, Widget

class Axel(object):
    load = js_function('axel.load')
    register = js_function('axel.register')
    ready = js_function('axel.ready')


class _ScriptLink(Link):
    no_inject = True

    @classmethod
    def guess_modname(cls):
        try:
            frame, i = inspect.stack()[0][0], 0
            while frame.f_globals['__name__'].startswith('axf.axel') or \
                    frame.f_globals['__name__'].startswith('tw2.core'):
                frame, i = inspect.stack()[i][0], i + 1

            return frame.f_globals['__name__']
        except Exception:
            return None

    @classmethod
    def post_define(cls):
        if getattr(cls, 'filename', None):
            if not cls.modname:
                cls.modname = cls.guess_modname()
            middleware.register_resource(cls.modname or '__anon__', cls.filename, cls.whole_dir)

    def prepare(self):
        if not hasattr(self, 'link'):
            rl = core.request_local()
            resources = rl['middleware'].resources
            self.link = resources.resource_path(self.modname or '__anon__', self.filename)


class AxelScript(object):
    def __init__(self, name, link=None, callback=None, load=False):
        self.name = name
        self.link = link
        self.callback = callback
        self.load = load

    def add_calls(self, widget):
        if self.link is not None:
            if not self.link.startswith('http') and not self.link.startswith('//'):
                link = _ScriptLink(filename=self.link).req()
            else:
                link = _ScriptLink(link=self.link).req()

            link.prepare()
            widget.add_call(Axel.register(self.name, link.link))

        if self.callback is not None:
            func = js_function(self.callback)
            func_args = ['#%s' % widget.compound_id]
            if hasattr(widget, '_axel_callback_args'):
                func_args.extend(widget._axel_callback_args)
            widget.add_call(Axel.ready(self.name, js_callback(func(*func_args))))

        if self.load:
            widget.add_call(Axel.load(self.name))


class AxelStyle(AxelScript):
    def __init__(self, name, link=None):
        super(AxelStyle, self).__init__(name, link)

    def add_calls(self, widget):
        if self.link is not None:
            if not self.link.startswith('http') and not self.link.startswith('//'):
                link = _ScriptLink(filename=self.link).req()
            else:
                link = _ScriptLink(link=self.link).req()

            link.prepare()
            widget.add_call(Axel.register(self.name, link.link))

        widget.add_call(Axel.load(self.name))


class AxelWidgetMixin(object):
    axel_scripts = Param('Scripts to load with the widget', request_local=False)
    axel_styles = Param('Stylesheets to load with the widget', request_local=False)

    def axel_prepare(self, *args):
        self._axel_callback_args = args

        self.safe_modify('resources')
        for script in self.axel_scripts:
            script.add_calls(self)

        for style in self.axel_styles:
            style.add_calls(self)
