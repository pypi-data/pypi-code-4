# -*- coding: utf-8 -*-
from time import time
from serializer import dumps


class XML(object):
    def __init__(self):
        self.renderers = {}

    def __call__(self, info):
        def _render(value, system):
            request = system.get('request')
            #Getting time of rendering xml
            t = time()
            resp = dumps(value, self.renderers)
            t = abs(t - time())
            if request is not None:
                response = request.response
                response.content_type = 'application/xml'
                #If the param 'xml_render.timeit' was set to 'true', adding a header 'Xml-Rendering-Time' with the number of seconds that were spent for the creating of the output xml
                rendering_time = system['renderer_info'].settings.get('xml_render.timeit')
                if rendering_time == 'true':
                    response.headers['Xml-Rendering-Time'] = str(t) + ' seconds'
            return resp
        return _render

    def add_adapter(self, renderer_type, renderer_func):
        self.renderers[renderer_type] = renderer_func
