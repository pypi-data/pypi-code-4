# -*- coding: utf-8 -*-

import urllib2, base64, json


from .models import ALLOWED_MODELS

DEFAULT_MODEL = ALLOWED_MODELS.get('')

class PythonClient(object):

    def __init__(self, token = '', *args, **kwargs):
        """
        Cache the Token
        """
        self.token = token
        self.base_api_url = kwargs.pop('base_url', 'http://cms.pull4up.com.br/api/v1/')
        self.allowed_methods = ALLOWED_MODELS.keys()

    def set_header(self, request, token):
        request.add_header('Authorization', 'Basic %s:' % token)
        return request

    def call(self, model = DEFAULT_MODEL, api_call = None):
        token = base64.encodestring('%s' % self.token)

        request = urllib2.Request("%s%s" % (self.base_api_url, api_call or ""))
        request = self.set_header(request, token)

        response = urllib2.urlopen(request)
        data = json.loads(response.read())

        obj_list = []
        if 'results' in data:
            for data in data['results']:
                obj_list.append(model(self, data))

            return obj_list
        else:
            return model(self, data)

    def call_from_url(self, model, url):
        url = url.replace(self.base_api_url, '')
        return self.call(model, url)

    def __getattr__(self, method_name):

        def get(self, *args, **kwargs):
            model = ALLOWED_MODELS.get(method_name)

            if method_name.endswith('s'):
                return self.call(model, method_name)
            else:
                try:
                    id = kwargs['id']
                    api_call = '%s/%d/' % (method_name, id)

                    return self.call(model, api_call)

                except KeyError:
                    raise KeyError('Usage: client.section(id = <section_id>). If you want get all the sections, use client.sections()')

        return get.__get__(self)
