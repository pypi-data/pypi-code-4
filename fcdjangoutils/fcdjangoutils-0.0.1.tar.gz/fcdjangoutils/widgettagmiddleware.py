# -*- coding: utf-8 -*-
import threading
import re

class WidgetTagMiddleware(object):
    data = threading.local()
    var_re = re.compile(r'%WidgetTagMiddleware.([^%]*)%')

    def process_request(self, request):
        return None

    def process_view(self, request, view_func, view_args, view_kwargs):
        return None

    def process_response(self, request, response):
        if 'text/' in response['Content-Type']:
            try:
                for name, values in getattr(self.data, 'vars', {}).iteritems():
                    response.content = response.content.replace('%WidgetTagMiddleware.'+name+'%', ''.join(values.itervalues()).encode('utf-8'))
                response.content = self.var_re.sub('', response.content)
            except Exception, e:
                print e
                print response['Content-Type']
                print type(response.content)
                for name, values in getattr(self.data, 'vars', {}).iteritems():
                    print type(name), [type(v) for v in values.itervalues()]
                raise
        return response

    def process_exception(self, request, exception):
        return None

    @classmethod
    def _ensure(cls):
        if getattr(cls.data, 'vars', None) is None:
            cls.data.vars = {}

    @classmethod
    def add(cls, section, key, value):
        cls._ensure()
        if section not in cls.data.vars:
            cls.data.vars[section] = {}
        cls.data.vars[section][key] = value

    @classmethod
    def addjsfile(cls, filename):
        cls.add("head.javascript", filename, "<script id='%s' language='javascript' type='text/javascript' src='%s'></script>" % (filename, filename,))

    @classmethod
    def addieonlyjsfile(cls, filename):
        cls.add("head.javascript", filename, "<!--[if IE]><script id='%s' language='javascript' type='text/javascript' src='%s'></script><![endif]-->" % (filename, filename,))

    @classmethod
    def addcssfile(cls, filename):
        cls.add("head.css", filename, "<link id='%s' rel='stylesheet' type='text/css' href='%s' />" % (filename, filename,))

    @classmethod
    def addjs(cls, name, js):
        cls.add("head.javascript", name, "<script id='%s' language='javascript' type='text/javascript'>%s</script>" % (name, js))

    @classmethod
    def addcss(cls, name, css):
        cls.add("head.css", name, "<style id='%s' type='text/css'>%s</style>" % (name, css))

    @classmethod
    def adddialog(cls, name, html):
        cls.add("body.dialog", name, "<div id='%s'>%s</div>" % (name, html))
