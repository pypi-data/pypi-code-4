class WrongParamException(Exception):
    pass


class InvalidImpException(Exception):
    pass


class PysistorFactory(object):
    backends = {}
    configs = {}
    default = None

    @classmethod
    def from_yaml(cls, string, **kwargs):
        """ A convenience method for from_dict """
        pass

    @classmethod
    def from_ini(cls, string, prefix=None, **kwargs):
        """ A convenience method for from_dict """
        pass

    @classmethod
    def from_yaml_str(cls, string, **kwargs):
        """ A convenience method for from_dict """
        pass

    @classmethod
    def from_ini_str(cls, string, prefix=None, **kwargs):
        """ A convenience method for from_dict """
        pass

    def from_dict(self, **kwargs):
        """ Supply this function with a dictionary containing proper
        configuration information about a new backend and the backend will be
        initializaed """
        self._build_backend(**kwargs)

    def _build_backend(self,
                       name=None,
                       backend="pysistor.backends.MemoryBackend",
                       set_default=False,
                       **kwargs):
        """ Internally takes a configuration dictionary and builds a backend """
        parts = backend.split('.')
        backend_mod = '.'.join(parts[0:-1])
        backend_class = parts[-1]

        # Set a default name
        if name is None:
            name = backend_class

        # Make sure we don't start building a duplicated name
        if name in self.backends:
            raise AttributeError("There is already a backend with that name")

        try:
            module = __import__(backend_mod, fromlist=[backend_class])
        except ImportError:
            raise ImportError("Dotted path {0} given for your backend could not"
                              " be imported!")

        backend_cls = getattr(module, backend_class, None)

        # Do our class checks
        for func in ['store', 'expire', 'get']:
            if not callable(getattr(backend_cls, func, None)):
                raise InvalidImpException("Backend must implement correct "
                                          "methods")

        # Should raise a WrongParamException if caller didn't include valid
        # config
        inst = backend_cls(**kwargs)
        # Add to internal dict
        self.backends[name] = inst

        # setup our default if requested
        if set_default:
            self.default = inst

    def __getitem__(self, key):
        """ Allow easy access to different named backends """
        if key is None:
            return self.default

        try:
            return self.backends[key]
        except KeyError:
            raise KeyError("Requested backend '{0}' doesn't exist".format(key))

    def store(self, key, value, expire=None, backend=None, adapter=None):
        """ Allow user to store data in a specific backend, or the default
        backend if ommitted. """
        self[backend].store(key, value, expire, adapter=adapter)

    def expire(self, key, backend=None):
        """ Allow user to remove data in a specific backend, or the default
        backend if ommitted. """
        self[backend].expire(key)

    def expire_all(self, prefix="", adapter=None, backend=None):
        """ Allow user to remove data in a specific backend, or the default
        backend if ommitted. """
        self[backend].expire_all(prefix, adapter=adapter)

    def get(self, key, adapter=None, backend=None):
        """ Allow user to access data in a specific backend, or the default
        backend if ommitted. """
        return self[backend][key]

Pysistor = PysistorFactory()
