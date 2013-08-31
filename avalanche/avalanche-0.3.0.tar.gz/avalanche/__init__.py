""" Avalanche - Web Framework with a focus on testability and reusability

The MIT License
Copyright (c) 2012 Eduardo Naufel Schettino
see LICENSE for details

"""

__version__ = "0.3.0"


import copy
import traceback

from .params import _PARAM_VAR, NoValue



class AvalancheException(Exception):
    pass


# FIXME - make this configurable - document
def use_namespace(func):
    """decorator that add use_namespace=True to function"""
    func.use_namespace = True
    return func




class ConfigurableMetaclass(type):
    """adds an attribute (dict) 'a_config' to the class

    * when the class is created it merges the confing from base classes
    * collect config info from the class methods (using _PARAM_VAR)
    * calls classmethod set_config (used by subclasses to alter config values
      from base classes)
    """
    def __new__(mcs, name, bases, dict_):
        # create class
        _class = type.__new__(mcs, name, bases, dict_)

        config = {}

        # get config from base classes
        for base_class in reversed(bases):
            if hasattr(base_class, 'a_config'):
                config.update(copy.deepcopy(base_class.a_config))

        # get config values from builders decorators
        for attr_name in dict_.keys():
            # get a_param from method
            attr = getattr(_class, attr_name)
            a_params = getattr(attr, _PARAM_VAR, None)
            if not a_params:
                continue
            # add to config dict
            handler_config = config.setdefault(attr_name, {})
            for param in a_params:
                handler_config[param.obj_name] = param
        _class.a_config = config

        # modify config
        _class.set_config()
        return _class

    @classmethod
    def set_config(cls):pass


class AvaResponse:
    """base class for a returned value from a context builder that creates
    a response directly instead of a context dict"""
    pass



class Redirect(AvaResponse):
    def __init__(self, uri):
        self.uri = uri

    def __call__(self, handler):
        handler.redirect(self.uri)


class RedirectTo(AvaResponse):
    def __init__(self, handler_name, **kwargs):
        self.handler_name = handler_name
        self.params = kwargs
        self.stack = traceback.extract_stack()

    def __call__(self, handler):
        try:
            handler.redirect_to(self.handler_name, **self.params)
        except Exception as error:
            error.__obj_stack__ = self.stack
            raise error

class _AvalancheHandler(metaclass=ConfigurableMetaclass):
    """avalanche functionality.

    Users should not subclass this directly, use ``make_handler``
    """

    # @ivar context: (dict) with values computed on context_builders

    #: dict of named route parameters
    route_kwargs = None

    # TODO: support context_builders defined in a different class
    # this would allow make_handler combine many AvalancheHandler's without
    # subclassing them.

    #: list of context-builder method names used on GET requests
    context_get = ['a_get', ]

    #: list of context-builder method names used on POST requests
    context_post = ['a_post', ]

    #: A `renderer` instance
    renderer = None

    #: (string) path to jinja template to be rendered
    template = None


    def _convert_params(self, param_list):
        """convert params from HTTP string to python objects

         @param param_list: list of AvalancheParam
         @return dict
        """
        param_objs = {}
        for param in param_list:
            try:
                param_objs[param.obj_name] = param.get_value(self)
            except NoValue:
                pass
        return param_objs


    def _builder(self, name):
        """retrieve builder method, give precise error messages if fails"""
        try:
            return getattr(self, name)
        except TypeError:
            msg_str = ("Error on handler '%s' context builder list contains " +
                   "an item with wrong type. " +
                   "List must contain strings with method names, " +
                   "got (%s: %r).")
            msg = msg_str % (self.__class__.__name__, type(name), name)
            raise AvalancheException(msg)


    def _build_context(self, builders):
        """build context for given builders

        @param builders: list of string of builder method names

        Values are saved in the `context` attribute.

        @return None to use handler Renderer, or an AvaResponse
        """

        # build context
        self.context = {}
        for builder_name in builders:
            #print "LOG:", self, builder_name
            builder = self._builder(builder_name)
            # get builder specific obj_params
            if builder_name in self.a_config:
                a_params = self.a_config[builder_name].values()
                param_objs = self._convert_params(a_params)
            else:
                param_objs = {}

            # run builder
            try:
                built_context = builder(**param_objs)
            except TypeError as exception:
                wrong_number_py3 = '%s() missing' % builder.__name__
                wrong_number = '%s() takes exactly' % builder.__name__
                unexpected_arg = 'got an unexpected keyword argument'
                if ((wrong_number not in str(exception)) and
                    (wrong_number_py3 not in str(exception)) and
                    (unexpected_arg not in str(exception))):
                    # should catch only:
                    # TypeError:"xxx() missing Y required positional argument"
                    # TypeError:"xxx takes exactly X arguments (Y given)"
                    # TypeError:"xxx() got an unexpected keyword argument 'yyy'
                    raise
                msg_str = ("Error: incomplete parameters for builder" +
                           " '%s.%s'. Got params %r, (Original error:%s)")
                msg = msg_str % (self.__class__.__name__, builder.__name__,
                                 param_objs, str(exception))
                raise AvalancheException(msg)

            # update handler context
            if isinstance(built_context, AvaResponse):
                return built_context
            if getattr(builder, 'use_namespace', False):
                # use namespace
                self.context[builder_name] = built_context
            else:
                if built_context is not None:
                    self.context.update(built_context)


    def render(self, **context):
        self.renderer.render(self, **context)


    def get(self, *args, **kwargs):
        """
          * build context
          * render template
        """
        self.route_kwargs = kwargs
        resp = self._build_context(self.context_get)
        if resp:
            resp(self)
        else:
            self.render(**self.context)

    def post(self, *args, **kwargs):
        """build_context should redirect page"""
        self.route_kwargs = kwargs
        resp = self._build_context(self.context_post)
        if resp:
            resp(self)
        # FIXME
        # else:
        #    5/0 # must return a response



class BaseHandler(metaclass=ConfigurableMetaclass):
    """Base class that user should subclass when creating request handlers"""

    @classmethod
    def set_config(cls):
        """used to modify config values inherited from a base class

        config values are saved as a dict in the attribute 'a_config'.

         * on first level keys are the name of config-builders
         * on second level keys are the parameter names
         * values are instances of AvalancheParam

        ::

          class MyHandler(MyHandlerBase):
              @classmethod
              def set_config(cls):
                  cls.a_config['builder_a']['x'] = avalanche.UrlQueryParam('x', 'x2')
        """
        pass




def _Mixer(class_name, bases, dict_=None):
    """create a new class/type with given name and base classes"""
    return type(class_name, bases, dict_ or {})


def make_handler(request_handler, app_handler, dict_=None):
    """creates a concrete request handler
     => ApplicationHandler(avalanche.Handler) + _AvalancheHandler +
     core.RequestHandler
    """
    handler_name = app_handler.__name__ + 'Handler'
    bases = (app_handler, request_handler, _AvalancheHandler)
    return _Mixer(handler_name, bases, dict_)
