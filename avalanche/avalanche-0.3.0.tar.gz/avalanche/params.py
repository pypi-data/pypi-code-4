# name of the variable added to context_builders to hold
# list of AvalancheParam
_PARAM_VAR = '_a_params'


class NoValue(Exception):
    """Exception used when AvalancheParam does not produce any value"""
    pass


class AvalancheParam:
    """A parameter converter - (Abstract base class)

    This is used to convert parameters (i.e. from the URL) from string to its
    real type.

    :param obj_name: name of param to be passed to context_builders
    :type obj_name: str

    """

    def __init__(self, obj_name):
        self.obj_name = obj_name

    def __call__(self, func):
        """when an object is used as a decorator adds itself in list
        variable in the decorated function"""
        if not hasattr(func, _PARAM_VAR):
            setattr(func, _PARAM_VAR, [])
        getattr(func, _PARAM_VAR).append(self)
        return func

    def __repr__(self):
        return "<%s:%s>" % (self.__class__.__name__, self.obj_name)

    def get_value(self, request): # pragma: no cover
        """return a value taken from request"""
        raise NotImplementedError



###### Param sources

class UrlPathParam(AvalancheParam):
    """get parameter from URL path (given by route)

    :param str_name: name of param on the source
                     if not provided use same as obj_name
    :type str_name: str

    :param str2obj: callable that converts param string to an object
                    if not provided obj it just returns the str_value
                    there are 2 acceptable signatures for the callable:

                     * take a single param with the str_value
                     * first param takes str_value, second is named 'handler'
                       and receives a reference to the RequestHandler

    """
    def __init__(self, obj_name, str_name=None, str2obj=None):
        self.obj_name = obj_name
        self.str_name = str_name or obj_name
        self.str2obj = str2obj

    def get_value(self, handler):
        str_value = self.get_str_value(handler)
        if str_value is not None:
            return self.str2obj(str_value) if self.str2obj else str_value
        raise NoValue()

    def get_str_value(self, handler):
        return handler.route_kwargs.get(self.str_name)


class UrlQueryParam(UrlPathParam):
    """get parameter from the URL query string"""
    def get_str_value(self, handler):
        return handler.request.GET.get(self.str_name, None)


class PostParam(AvalancheParam):
    """get a dictionary with all POST params"
    """
    def get_value(self, handler):
        return handler.request.POST.copy()


class GetParam(AvalancheParam):
    """get a dictionary with all GET params"
    """
    def get_value(self, handler):
        return handler.request.GET.copy()


class PostGroupParam(AvalancheParam):
    """get a dictionary with all paramaters which name starts with "<str_name>-"
    """
    def __init__(self, obj_name, str_name=None):
        self.obj_name = obj_name
        self.str_name = str_name or obj_name

    def get_value(self, handler):
        data = {}
        prefix = '%s-' % self.str_name
        prefix_len = len(prefix)
        POST = handler.request.POST
        for arg in POST.iterkeys():
            if arg.startswith(prefix):
                name = arg[prefix_len:]
                data[name] = POST.get(arg)
        return data



class ContextParam(AvalancheParam):
    """get param from request-handler context"""
    def __init__(self, obj_name, str_name=None):
        self.obj_name = obj_name
        self.str_name = str_name or obj_name

    def get_value(self, handler):
        return handler.context[self.str_name]
