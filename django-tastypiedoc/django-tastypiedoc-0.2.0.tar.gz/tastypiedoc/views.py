# Create your views here.
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.conf import settings
import json


class AbstractEntityFactory(object):

    def get_entity_type(self, u):
        return u['namespace'].split(':')[-1]


    def get_url(self, u):
        return settings.TASTYPIEDOC['api_root'] + '/'.join(u['namespace'].split(':')[1:])

    def get_list_url_kwargs(self, u):
        kwargs = []
        namespace_tokens = u['namespace'].split(':')[1:]
        parameterized_url = None
        for tok in namespace_tokens:
            if not tok == self.entity_type:
                kwargs.append(tok)

                #Parameterize the url
                url_tok = '%s/' % tok
                tok_param = '%s_kwarg' % tok
                split_url = self.url.split(url_tok)
                before_tok = split_url[0]
                after_tok = split_url[1]
                self.url = '%s%s{%s}/%s' % (before_tok, url_tok, tok_param, after_tok)

        return kwargs

    def get_detail_url_kwargs(self, u):
        kwargs = self.get_list_url_kwargs(u)
        kwargs.append('pk')
        self.url = self.url + '/{pk_kwarg}'
        return kwargs


    def create_entity_api_dispatch_list(self, u):
        self.entity_type = self.get_entity_type(u)
        self.url = self.get_url(u)
        self.namespace = u['namespace']
        self.name = "List %s" % self.entity_type
        self.method = 'list'
        self.kwargs = self.get_list_url_kwargs(u)



    def create_entity_api_dispatch_detail(self, u):
        self.entity_type = self.get_entity_type(u)
        self.url = self.get_url(u)
        self.namespace = u['namespace']
        self.name = "Get %s" % self.entity_type
        self.method = 'detail'
        self.kwargs = self.get_detail_url_kwargs(u)


    #TODO functionality for set endpoints
    # def create_entity_api_get_multiple(self, u):
    #     self.entity_type = self.get_entity_type(u)
    #     self.url = self.get_url(u) + '/set'
    #     self.namespace = u['namespace']
    #     self.name = "Get multiple %s" % self.entity_type
    #     self.method = 'set'
    #     self.kwargs = self.get_list_url_kwargs(u)


    def create_entity_api_get_schema(self, u):
        self.entity_type = self.get_entity_type(u)
        self.url = self.get_url(u) + '/schema'
        self.namespace = u['namespace']
        self.name = "Schema of %s" % self.entity_type
        self.method = 'schema'
        self.kwargs = self.get_list_url_kwargs(u)


    def create(self, u):
        method_name = 'create_entity_%s' % u['name']
        method = getattr(self, method_name, None)
        if method:
            method(u)
            return self
        return None







class ApiDisplay(object):


    def __init__(self, urls):
        self.entity_groups = {}
        self.parameterize_entities(urls)


    def create_entity(self, u):
        ent = AbstractEntityFactory().create(u)
        return ent


    def parameterize_entities(self, urls):
        for u in urls:
            ent = self.create_entity(u)
            if ent:
                group = self.entity_groups.get(ent.entity_type, {'entity_type' : ent.entity_type, 'methods' : []})
                group['methods'].append(ent)
                self.entity_groups[ent.entity_type] = group

        self.entity_groups = self.entity_groups.values()


    def index(self, request):
        return render_to_response('index.html', {
            'entities' : self.entity_groups,
            'tastypiedoc_settings' : json.dumps(settings.TASTYPIEDOC)
        }, RequestContext(request))