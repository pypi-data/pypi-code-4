from itertools import count
from functools import reduce

__version__ = '0.1'


class Factory(object):

    _creation_order = count()

    def __init__(self, what, *args, **kwargs):

        for name in ['configure_object', 'create_object', 'destroy_object']:
            meth = kwargs.pop(name, None)
            if meth is not None:
                setattr(self, '_' + name, meth)

        self.what = what
        self.args = args
        self.kwargs = AttrDict(kwargs)
        self._order = next(self._creation_order)

        # process subfactory__attribute='foo'
        for k, v in list(self.kwargs.items()):
            if '__' in k:
                head, tail = k.split('__', 1)
                self.kwargs[head] = self.kwargs[head](**{tail: v})
                del self.kwargs[k]

    def __getattr__(self, attr):
        return Lazy(self, attr)

    def __setitem__(self, attr, value):
        if '.' in attr:
            head, tail = attr.split('.', 1)
            self.kwargs[head] = self.kwargs[head](**{tail: value})
        else:
            self.kwargs[attr] = value

    def __getitem__(self, attr):
        return Lazy(self, attr)

    def __call__(self, *args, **kwargs):
        return self.__class__(self.what,
                              *(args or self.args),
                              **dict(self.kwargs, **kwargs))

    def __get__(self, instance, context):
        """
        Factories have magic behaviour in the context of fixtures, so that
        accessing 'my_fixture.foo' auto-delegates to 'my_fixture.o.foo'
        """
        if isinstance(instance, Fixture):
            try:
                return instance.o[instance.factory_names[self]]
            except KeyError:
                raise AttributeError()
        return self

    def create_object(self, context):
        args = tuple(context.resolve(a) for a in self.args)
        kwargs = dict((k, context.resolve(v)) for k, v in self.kwargs.items())

        ob = self._create_object(context, args, kwargs)
        ob = self._configure_object(ob, context)
        return ob

    def destroy_object(self, context, ob):
        return self._destroy_object(context, ob)

    def _create_object(self, context, args, kwargs):
        return self.what(*args, **kwargs)

    def _destroy_object(self, context, ob):
        pass

    def _configure_object(self, ob, context):
        return ob

    @classmethod
    def setup_complete(self, context, created):
        """\
        Override this in subclasses to implement custom behaviour after all
        objects have been created (eg flushing to database)
        """


class CallFactory(Factory):
    """\
    A factory that returns the value of a callable function or object.

    Use this to lazily instantiate values that are accessible at setup
    time but not necessarily earlier::

        class fixture(Fixture):

            user = CallFactory(lambda: User.objects.get(username='admin'))
            ...

    """

    def _create_object(self, context, args, kwargs):
        return self.what(*args, **kwargs)

    def _destroy_object(self, context, ob):
        pass


class DjangoFactory(Factory):

    def _create_object(self, context, args, kwargs):
        ob = self.what.objects.create(*args, **kwargs)
        ob.save()
        return ob

    def _destroy_object(self, context, ob):
        ob.delete()


class StormFactory(Factory):
    """\
    Typically you would configure this in at the start of your test code, so::

        getstore = lamdba: getUtility(IZStorm).get('main'))
        Factory = StormFactory.configure(getstore)

    You can then use Factory as normal::

        class fixture(Fixture):
            user = Factory(models.User, ...)

    By default, StormFactory call ``store.flush`` but not ``store.commit``.
    Change this behaviour by passing factory options to setup::

        fixture.setup(flush=False)
        fixture.setup(commit=True)

    """

    #: Callable that can retrieve Storm's store object.
    getstore = lambda: None

    storekey = '_StormFactory_store'

    @classmethod
    def configure(cls, getstore):
        return type('StormFactory', (StormFactory,),
                    {'getstore': staticmethod(getstore)})

    @classmethod
    def _getstore_cached(cls, context):
        try:
            return context.factoryoptions[cls.storekey]
        except KeyError:
            return context.factoryoptions.setdefault(cls.storekey,
                                                     cls.getstore())

    def _create_object(self, context, args, kwargs):
        store = self._getstore_cached(context)
        ob = self.what.__new__(self.what)
        for item, value in kwargs.items():
            setattr(ob, item, value)
        if store is not None:
            store.add(ob)
        return ob

    def _destroy_object(self, context, ob):
        store = self._getstore_cached(context)
        if store is not None:
            store.remove(ob)

    @classmethod
    def setup_complete(cls, context, created):
        store = cls._getstore_cached(context)
        if store:
            if context.factoryoptions.get('flush', True):
                store.flush()
            if context.factoryoptions.get('commit', False):
                store.commit()


class ArgumentGenerator(object):
    """
    A callable that dynamically generates factory arguments
    """

    def __init__(self, fn):
        self.fn = fn

    def __call__(self):
        return self.fn()


class ArgumentGeneratorFactory(object):
    """
    A factory for producing ``ArgumentGenerator`` objects.

    For an example, see :class:`~toffee.Seq`
    """

    def make_argument_generator(self):
        raise NotImplementedError


class Seq(ArgumentGeneratorFactory):

    def __init__(self, str_or_fn='%d', start=0):
        self.str_or_fn = str_or_fn
        self.start = start

    def make_argument_generator(self):
        counter = count(self.start)

        def seq():
            n = next(counter)
            if callable(self.str_or_fn):
                return self.str_or_fn(n)
            else:
                return self.str_or_fn % (n,)
        return ArgumentGenerator(seq)


class Lazy(object):
    def __init__(self, factory, attrs):
        self.factory = factory
        if not isinstance(attrs, list):
            attrs = [attrs]
        self.attrs = attrs

    def __getattr__(self, attr):
        return Lazy(self.factory, self.attrs + [attr])

    def __str__(self):
        return "<%s for %r %r>" % (self.__class__.__name__, self.factory,
                                   '.'.join(self.attrs))
    __repr__ = __str__


class AttrDict(dict):

    def __getattr__(self, item):
        return self[item]

    def __setattr__(self, item, value):
        self[item] = value


class Fixture(object):

    def __init__(self, **kwargs):

        #: Factory definitions
        self.d = AttrDict()
        self.factory_names = {}

        #: Factory-created objects
        self.o = AttrDict()
        self.created = None

        class_factories = ((k, getattr(self.__class__, k))
                           for k in dir(self.__class__))
        class_factories = ((k, v)
                           for k, v in class_factories
                           if isinstance(v, Factory))

        self.update_factories(dict(class_factories, **kwargs))

    def __getattr__(self, name):
        try:
            return self.o[name]
        except KeyError:
            raise AttributeError(name)

    def update_factories(self, factories):
        for k, v in factories.items():
            if v in self.factory_names:
                raise ValueError("Factory %r used more than once (%r and %r)" %
                                 (v, k, self.factory_names[v]))
            self.factory_names[v] = k
        self.d.update(factories)

    def setup(self, force=False, **factoryoptions):
        """
        :param force: allow calls to setup to be nested
        :param **factoryoptions: any factory specific options, for example
                                 passing flags such as ``commit=True``. See
                                 individual factory subclasses for information
        """
        if self.created and not force:
            raise Exception("setup() has already been called on this fixture. "
                            "Call teardown first, or use setup(force=True).")

        self.factoryoptions = factoryoptions
        self.o = AttrDict()
        self.created = []
        self.argument_generators = {}

        factories = sorted((v._order, k) for k, v in self.d.items())
        for _, name in factories:
            self._get_or_create_named_object(name)
        self.setup_complete()
        return self

    def setup_complete(self):
        """\
        Call any setup_complete methods on factory classes to let them know
        that all objects have been created
        """
        factory_created = {}

        for name, ob, factory in self.created:
            factory_created.setdefault(factory.__class__, []).append(ob)

        for f, obs in factory_created.items():
            f.setup_complete(self, obs)

        self.configure()

    def configure(self):
        """\
        Subclasses should override this to provide custom post-creation
        configuration
        """

    def _get_or_create_named_object(self, name):
        """\
        Return the object from the named factory, creating it if necessary
        """
        try:
            return self.o[name]
        except KeyError:
            pass
        return self._create_object_from_factory(self.d[name])

    def _create_object_from_factory(self, factory):
        """\
        Invoke ``factory`` to create and configure an object.
        Register the created object so that it may later be referenced and
        torn down.
        """
        ob = factory.create_object(self)
        name = self.factory_names.get(factory, None)
        if name is not None:
            self.o[name] = ob
        self.created.append((name, ob, factory))
        return ob

    def resolve(self, what):

        if isinstance(what, ArgumentGeneratorFactory):
            if what not in self.argument_generators:
                self.argument_generators[what] = \
                        what.make_argument_generator()
            return self.argument_generators[what]()

        if isinstance(what, ArgumentGenerator):
            return what()

        if isinstance(what, Factory):
            return self.resolve(Lazy(what, []))

        if isinstance(what, Lazy):
            if what.factory in self.factory_names:
                name = self.factory_names[what.factory]
                ob = self._get_or_create_named_object(name)
            else:
                ob = self._create_object_from_factory(what.factory)

            return reduce(getattr, what.attrs, ob)

        return what

    def teardown(self):
        while self.created:
            name, ob, factory = self.created.pop()
            if name is not None:
                del self.o[name]
            factory.destroy_object(self, ob)
        self.factoryoptions = {}

    def __enter__(self, *args, **kwargs):
        return self.setup(*args, **kwargs)

    def __exit__(self, type, value, tb):
        if type:
            try:
                self.teardown()
            except Exception:
                pass
        else:
            self.teardown()
        return False

    #: Alias for compatility with unittest names
    setUp = setup

    #: Alias for compatility with unittest names
    tearDown = teardown
