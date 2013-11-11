
import json
from jinja2 import Environment, FileSystemLoader

class View:
    headers = {}
    body = ''
    
    def __init__(self, *args, **kwargs):
        
        self.handler = args[0]
        self.context = args[1]
        self.data    = args[2]
        
        self._ = self.handler._
    
    def no_cache_header(self):
        self.headers['Pragma']  = 'no-cache'
        self.headers['Expires'] = '0'
        self.headers['Cache-Control'] = 'must-revalidate, post-check=0, pre-check=0'
        
    def render(self):
        return self.body
    
class JsonView(View):

    def __init__(self, *args, **kwargs):
        self.headers['Content-Type'] = 'application/json'
        View.__init__(self, *args, **kwargs)
    
    def render(self):
        return json.dumps(self.data)
    


class Path(list):
    @property
    def next(self):
        return self.pop(0)


class HtmlView(View):

    def __init__(self, *args, **kwargs):
        View.__init__(self, *args, **kwargs)
        
        self.headers['Content-Type'] = 'text/html; charset="utf-8"'
        self.no_cache_header()
        
        ext = ['jinja2.ext.with_', 'jinja2.ext.i18n','jinja2.ext.do']
        if not self.handler.settings.get('debug'):
            ext.append('ramen.jinja2htmlcompress.HTMLCompress')
        
        self.jinja2 = Environment(
            loader = FileSystemLoader(self.handler.settings['template_path']),
            extensions = ext,
            trim_blocks = True
        )
    
    def render(self):
        data = self.data
        data.update(self.context)
        data['_'] = self._
        
        path = ''
        path_list = Path([])
        for namespace in self.handler.initkw.pop('namespaces', []):
            path = '%s%s/' % (path, namespace)
            path_list.append('%s_wrapper.html' % path)
        
        path_list.append(self.handler.template_name)
        data['template'] = path_list
        
        t = self.jinja2.get_template(self.handler.template_root)
        return t.render(**data)

class JScriptView(View):

    def __init__(self, *args, **kwargs):
        self.headers['Content-Type'] = 'application/x-javascript; charset="UTF-8"'
        View.__init__(self, *args, **kwargs)
