__author__ = 'chimezieogbuji'



import hashlib
from wheezy.http.cache import etag_md5crc32
from wheezy.caching.patterns import Cached
from wheezy.http.middleware import http_cache_middleware_factory
from wheezy.http.middleware import environ_cache_adapter_middleware_factory
from wheezy.http.middleware import wsgi_adapter_middleware_factory
from wheezy.caching.memcache import MemcachedClient
from wheezy.http import bootstrap_http_defaults, CacheProfile, WSGIApplication
from datetime import timedelta

class memcached(object):
    """
    Decorator that uses memcache to cache response to
    calling the function where the key is based on
    the values of the arguments given

    modified from http://www.zieglergasse.at/blog/2011/python/memcached-decorator-for-python/
    """
    def __init__(self,memcache_socket):
        self.memcache_socket = memcache_socket

    def __call__(self, f):

        def newfn(*args, **kwargs):
            mc = MemcachedClient([self.memcache_socket], debug=0)
            # generate md5 out of args and function
            m = hashlib.md5()
            margs = [x.__repr__() for x in args]
            mkwargs = [x.__repr__() for x in kwargs.values()]
            map(m.update, margs + mkwargs)
            m.update(f.__name__)
            m.update(f.__class__.__name__)
            key = m.hexdigest()

            value = mc.get(key)
            if value:
                return value
            else:
                value = f(*args, **kwargs)
                mc.set(key, value, 60)
                return value
        return newfn


def normalize_to_list(item):
    if item is None:
        return []
    else:
        return item if isinstance(item,list) else [item]

class WheezyCachingAdapterSetup(object):
    def __init__(self,
                 cache_location='public',
                 static_dependency = None,
                 queries = None,
                 ttl=15,
                 debug=False,
                 max_age=None,
                 memcache_socket = 'unix:/tmp/memcached.sock'):
        """
        Used as an Akara WSGI wrapper, i.e.:
        @simple_service(...,wsgi_wrapper=WheezyCachingAdapterSetup( ... ))

        Produces a wheezy.http.WSGIApplication that implements HTTP caching

        cache_location is used for the CacheProfile
        ( see: http://pythonhosted.org/wheezy.http/userguide.html#cache-location )

        static_dependency indicates the name of a master_key for a CacheDependency associated
        with the wrapped Akara service
        ( see: http://pythonhosted.org/wheezy.caching/userguide.html#cachedependency )

        queries is a list of query key's that will be used to compose the key for caching
        responses to requests

        ttl is the time to live for the content  (server) caching in seconds

        IF specified, max_age is used on the policy to set the corresponding
        HTTP cache control header (an indication to accept a response whose age
        is no greater than the specified time in seconds)

        memcache_socket is the memcache socket to use for content caching purposes

        Within an Akara service decorated in this way, a wheezy.http.HTTPCachePolicy instance can be created:

            profile = request.environ['wheezy.http.cache_profile']
            policy = profile.cache_policy()

        And then its various methods can be used to control cache-specific HTTP headers
        of the response:
            See: http://packages.python.org/wheezy.http/userguide.html#cache-policy

        Then request.environ['wheezy.http.cache_policy'] needs to be set to the policy:

            request.environ['wheezy.http.cache_policy'] = policy

        As an alternative to providing a static dependency name via the static_dependency
        keyword argument, a dependency with a dynamic master key can be provided via:

            request.environ['wheezy.http.cache_dependency'] = ['.. cache name ..', ..., ]

        Cache can be invalidated by (dependency) name via:

            request.environ['akamu.wheezy.invalidate']('..cache name..')

        """
        assert cache_location in ['none','server','client','public']
        self.cache              = MemcachedClient([memcache_socket])
        self.cache_location     = cache_location
        self.debug              = debug
        self.cached             = Cached(self.cache, time=ttl)
        self.static_dependency  = static_dependency
        self.max_age            = max_age
        self.cache_profile = CacheProfile(
            cache_location,
            vary_query=queries,
            enabled=True,
            etag_func=etag_md5crc32,
            duration=timedelta(seconds=ttl))

    def __call__(self,akara_application):
        """
        Called by Akara to provide the akara application
        as a WSGI application to be 'wrapped'

        Returns a wsgi_application that wraps the akara service and facilitating
        the use of WSGI environ variables for http content caching middleware.
        """
        self.akara_application = akara_application

        def wsgi_wrapper(environ, start_response):
            if self.cache_location != 'none':
                environ['wheezy.http.cache_profile'] = self.cache_profile
            def InvalidateCacheViaDependency(cacheName):
                from wheezy.caching.dependency import CacheDependency
                dependency = CacheDependency(
                    self.cache,
                    # namespace=self.cache_profile.namespace
                )
                if self.debug:
                    print "###","Invalidating cache: ", cacheName,"###"
                dependency.delete(cacheName)
                # self.cached.delete(cacheName)

            #Provide hook for cache dependency invalidation to akara service
            environ['akamu.wheezy.invalidate']     = InvalidateCacheViaDependency

            if self.debug:
                print "###","Calling akara application from wheezy.http","###"

            rt = akara_application(environ, start_response)
            if 'wheezy.http.cache_dependency' in environ:
                item = environ['wheezy.http.cache_dependency']
                environ['wheezy.http.cache_dependency'] = normalize_to_list(item)
                if self.debug:
                    print "###","Dependency key(s): ", environ['wheezy.http.cache_dependency'],"###"
            elif self.static_dependency:
                environ['wheezy.http.cache_dependency'
                ] = normalize_to_list(self.static_dependency)
                if self.debug:
                    print "###","Dependency key(s): ", self.static_dependency,"###"
            if self.max_age is not None:
                if self.debug:
                    print "###","Setting max_age and etag via function","###"
                policy = self.cache_profile.cache_policy()
                policy.max_age(self.max_age)
                policy.etag(self.cache_profile.etag_func(rt))
            return rt

        return WSGIApplication([
                bootstrap_http_defaults,
                http_cache_middleware_factory,
                environ_cache_adapter_middleware_factory,
                wsgi_adapter_middleware_factory
            ],
            {
                 'wsgi_app' : wsgi_wrapper,
                'http_cache': self.cache
            }
        )