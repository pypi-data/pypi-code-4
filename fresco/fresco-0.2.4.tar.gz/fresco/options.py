class Options(dict):
    """\
    Options dictionary. An instance of this is attached to each
    :class:`fresco.core.FrescoApp` instance, as a central store for
    configuration options.
    """

    def __getattr__(self, name):
        return self[name]

    def __setattr__(self, key, value):
        self[key] = value

    def update_from_file(self, path):
        """
        Update the instance with any symbols found in the python source file at
        `path`.
        """
        with open(path, 'r') as f:
            source = f.read()
            config_code = compile(source, f.name, 'exec')
        ns = {'__file__': path, 'options': self}
        exec config_code in ns
        del ns['__file__']
        del ns['options']
        self.update(ns)

    def update_from_object(self, ob):
        """
        Update the instance with any symbols listed in object `ob`
        """
        self.update(dict((k, getattr(ob, k)) for k in dir(ob)))
