from werkzeug.wrappers import Response
from jinja2 import Environment, FileSystemLoader
from simplejson import JSONEncoder as encoder
import os


class Renderer(object):
    """Render the templates.
    """

    extension_accepted = ['html', 'json', 'xml']

    def __init__(self):
        self.template_path = os.path.join(os.path.dirname(__file__),
                                          'templates')
        loader = FileSystemLoader(self.template_path)
        self.jinja_env = Environment(loader=loader, autoescape=True)

    def __call__(self, view, req, data, resp=None):
        return self._render_template(view.template_name, data, resp,
                                     req.accept_mimetypes.best)

    def _render(self, data, file_ext, template_path):
        if file_ext == 'json':
            res = encoder().encode
        else:
            t = self.jinja_env.get_template(template_path)
            res = t.render
        return res

    def _render_template(self, template_name, data, response, mimetype):
        file_ext = mimetype.split('/')[1]
        #To avoid rendering some unknown file
        if not file_ext in self.extension_accepted:
            #TODO: raise an appropriate exception
            return

        template_path = "".join((template_name, '.', file_ext))
        render = self._render(data, file_ext, template_path)
        if response is None:
            response = Response(render(data),  mimetype=mimetype)
        return response
