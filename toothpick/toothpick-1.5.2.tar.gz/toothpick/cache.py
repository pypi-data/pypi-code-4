import toothpick

from toothpick import logger
from toothpick import exceptions

from functools import wraps

from werkzeug.contrib.cache import NullCache, BaseCache

class CacheError(Exception): pass

backend = NullCache()
log_actions = []

def default_cache_key(f, *args, **kwargs):
    '''Function used to make cache keys for the `cached` decorator'''
    return "%s%s%s" % (f.__name__, args, kwargs)


def _log(method, key, **extras):
    if method in log_actions:
        extra = ""
        if extras:
            extra = "(%s)" % " ".join(["%s=%s" % item 
                                       for item in extras.items()])
        logger.info(
            "CACHE %s: %s%s" % (
                method,
                key,
                extra
            )
        )

def get(key):
    _log("GET", key)
    return backend.get(key)

def set(key, value, timeout=None):
    _log("SET", key, value=value, timeout=timeout)
    return backend.set(key, value, timeout=timeout)

def delete(key):
    _log("DELETE", key)
    return backend.delete(key)

def set_backend(object_or_string, **cache_kwargs):
    global backend
    if isinstance(object_or_string, BaseCache):
        cache_object = object_or_string
    else:
        try:
            object_or_string = object_or_string.rsplit('.', 1)
            module = object_or_string[0]
            cls = object_or_string[1]
            backend_module = __import__(module, fromlist=[cls])
            cache_object = getattr(backend_module, cls)(**cache_kwargs)

        except AttributeError, e:
            raise CacheError(
                '''Backend must be a werkzeug.contrib.cache.BaseCache subclass
                instance or a string describing the full module path to such a
                subclass.'''
            )
        except ImportError, e:
            raise CacheError("Couldn't import %s" % object_or_string)
        except TypeError:
            raise CacheError("Bad argument list for backend: %s.%s(%s)" % \
                             (module, cls, cache_kwargs))

    backend = cache_object



# Decorators below

def cached(ttl=None, cache_key=None):
    def with_cache(f):
        @wraps(f)
        def closure(*args, **kwargs):
            key = closure.cache_key(f, *args, **kwargs)

            value = get(key)
            if value is None:
                value = f(*args, **kwargs)
                set(key, value, timeout=closure.ttl)

            return value


        if callable(cache_key):
            closure.cache_key = cache_key
        else:
            closure.cache_key = default_cache_key

        closure.uncached = f
        closure.ttl = ttl
        return closure

    return with_cache

def cached_resource(model_class, ttl=None, cache_key=None):
    '''
    Exactly like the `cached` decorator, but assumes that the closure around
    the original function is going to get a resource name, and other resource
    accoutrements
    '''
    def with_cache(f):
        @wraps(f)
        def closure(self, resource_name, query, *args, **kwargs):
            # we're bypassing proxying here - if you set an option on a
            # resource, then even if the data is eventually going to go through
            # another resource, the options on the named resource should be the
            # ones in play.
            options = model_class._resources[resource_name].options

            # check for resource-based cache exemption
            if not options.get('cached', True):
                return f(self, resource_name, query, *args, **kwargs)
            
            # resource-based ttl override
            ttl = options.get('cache_ttl', closure.ttl)

            key = closure.cache_key(f, resource_name, query, *args, **kwargs)

            value = get(key)
            if value is None:
                value = f(self, resource_name, query, *args, **kwargs)
                set(key, value, timeout=ttl)

            return value


        if callable(cache_key):
            closure.cache_key = cache_key
        else:
            closure.cache_key = default_cache_key

        closure.uncached = f
        closure.ttl = ttl
        return closure

    return with_cache


def cached_model(ttl=None, cache_key=None):
    '''
    Perform model-based caching. Toothpick-based classes decorated
    with this method will fetch the underlying document from cache,
    if possible, before falling back to traditional fetching. If a `ttl`
    parameter is provided, it will override the default ttl of the cache
    backend.
    
    The cache key used is based on the (class, resource_name, query) tuple that
    make up a call to fetch_doc, so two different instances of a cached model
    that both refer to the same document or documents will both be populated
    with cache data.
    '''

    def closure(model_class):
        from toothpick.concerns.cacheable import Cacheable
        from toothpick.concerns.findable import Findable
        if not issubclass(model_class, (Cacheable, Findable)):
            raise exceptions.ToothpickException(
                """Only classes inherititing the Findable and Cacheable
                concerns can be cached with this decorator."""
            )

        def model_cache_key(f, resource_name, query, options=None,
                            *args, **kwargs):
            '''Function used to make cache keys for the `cached_model` decorator'''
            if not options:
                options = {}

            return "toothpick/models/%s.%s(%s,%s,%s)" % (
                model_class._model_name(),
                f.__name__,
                resource_name,
                unicode(query),
                repr(options)
            )

        if callable(cache_key):
            key_function = cache_key
        else:
            key_function = model_cache_key


        cached_decorator = cached_resource(
            model_class=model_class, ttl=ttl, cache_key=key_function
        )
        model_class._fetch_docs = classmethod(
            cached_decorator(model_class._fetch_docs.im_func)
        )

        exists_decorator = cached_resource(
            model_class=model_class, ttl=ttl, cache_key=key_function
        )
        # `_document_exists` is already a class method, so a class argument is
        # already going to be prepended to the arguments.  To decorate a class
        # method, it seems like you need to grab the 'original' function
        # (unbound to the class), and decorate that, and then make it a
        # classmethod again, via the built-in decorator.  This is what I'm
        # doing below.
        model_class._document_exists = classmethod(
            exists_decorator(model_class._document_exists.im_func)
        )

        model_class._uses_toothpick_cache = True

        return model_class

    return closure

