import re
from django.conf.urls import patterns, url
from djrest.common.helpers import trailing_slash
from djrest.http.responses import HttpMethodNotAllowed


class RestApi(object):
    """
    Base rest api, contains the different resources and generates the corresponding urls.
    """
    def __init__(self, api_name="api"):
        self._resources = {}
        self.api_name = api_name

    def register_resource(self, resource):
        self._resources[resource.resource_name] = resource

    @property
    def base_url(self):
        return self.api_name + '/'

    @property
    def urls(self):
        urlpatterns = []
        pattern_list = []

        for resource in self._resources:
            for resource_method in self._resources[resource].methods:
                pattern_list.append(url(r"%s/%s%s%s$" % (resource_method.version,
                                                         self._resources[resource].resource_name,
                                                         resource_method.url, trailing_slash()),
                                        resource_method))
                if resource_method.allow_empty_args:
                    pattern_list.append(url(r"%s/%s%s%s$" % (resource_method.version,
                                                             self._resources[resource].resource_name,
                                                             resource_method.base_url, trailing_slash()),
                                            resource_method))

        urlpatterns += patterns('', *pattern_list)

        return urlpatterns


class Resource(object):
    """
    Resource class: This represents the current root resource that is being accessed.
    Holds the resource name, the versions submodules, and many settings that will be added
    in the future.

    The versions modules must define the resource operations, classes
    inheriting from Rest and implementing the HTTP Methods. These versions can be separated
    in different modules that will be mapped to the current resource url.

    """
    def __init__(self):
        self._versions_package = []
        self._methods = {}
        self.secure_methods = True

    def register_rest_operation(self, version, rest_op):
        ## validate version.
        if not re.match(r'^v[0-9]+$', version):
            raise ValueError("Version must match 'v[0-9].*'")
        rest_op.version = version
        ## Instantiate Rest class
        m_obj = rest_op()
        m_obj.rest_secure = self.secure_methods
        self._methods[id(m_obj)] = m_obj

    @property
    def methods(self):
        return [self._methods[_key] for _key in self._methods]


class Rest(object):
    """
    Rest operation container. Holds the basic GET/POST/PUT/PATCH/DELETE operation
    on a certain rest resource given a certain uri

    decorator usage:
        @route("/<id>/<name>/<etc>", methods=['POST', 'GET'], secure=False|True)

    secure = True -> Means that the authentication middleware will process this view
    """

    def __init__(self):
        self.csrf_exempt = True
        self.rest_secure = True

    @staticmethod
    def route(uri, methods=None, allow_empty_args=False, secure=True):
        valid_methods = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']
        if not methods:
            methods = []
        if uri[0] != '/':
            uri = '/' + uri

        def wrap(f):
            temp_url = uri
            f.__protected_rest_view = True
            f.__rest_secure = secure
            f.__supported_methods = [m for m in methods if m in valid_methods]
            if temp_url == "/":
                temp_url = ""
                base_url = ""
            else:
                tag_pos = temp_url.find(':')
                bracket_pos = temp_url.find('{')
                if bracket_pos >= 0:
                    base_url = temp_url[:(bracket_pos - 1)]
                else:
                    base_url = temp_url
                while tag_pos > 0:
                    arg_type = temp_url[tag_pos:tag_pos + 4]
                    if arg_type == ':int':
                        tag = r'\d+'
                    elif arg_type == ':str':
                        tag = r'\w+'
                    else:
                        raise ValueError('Incorrect argument type. Values are "int" or "str"')
                    temp_url = temp_url.replace(arg_type, '', 1).replace('{', '(?P<', 1).replace('}', '>%s)' % tag, 1)
                    tag_pos = temp_url.find(':')
                if tag_pos == -1 and re.match(".*{.*}.*""", temp_url):
                    raise ValueError('Missing argument type. Values are "int" or "str"')
            if allow_empty_args:
                f.allow_empty_args = True
            else:
                f.allow_empty_args = False
            f.base_url = base_url
            f.url = temp_url
            return f
        return wrap

    def __call__(self, request, *args, **kwargs):
        m_override = request.META.get('HTTP_X_HTTP_METHOD_OVERRIDE', None)
        allowed = getattr(self, '_Rest__supported_methods', [])
        request.method = m_override if m_override else request.method

        if request.method in allowed:
            return getattr(self, request.method.lower())(request, *args, **kwargs)
        else:
            response = HttpMethodNotAllowed()
            response["Allow"] = ''.join([("%s " % m).upper() for m in allowed])
            return response