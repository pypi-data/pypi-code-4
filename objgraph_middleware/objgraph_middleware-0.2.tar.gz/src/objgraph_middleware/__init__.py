from __future__ import absolute_import
import operator
import random
import gc
import logging
import json

from paste.wsgilib import add_close
from objgraph import typestats


log = logging.getLogger('objgraph_middleware')


def compute_growth(limit=10, peak_stats={}):
    gc.collect()
    stats = typestats()
    deltas = {}
    for name, count in stats.items():
        old_count = peak_stats.get(name, 0)
        if count > old_count:
            deltas[name] = count - old_count
            peak_stats[name] = count
    deltas = sorted(deltas.items(), key=operator.itemgetter(1),
                    reverse=True)
    if limit:
        deltas = deltas[:limit]
    return deltas


class ObjgraphMiddleware(object):

    def __init__(self, application, global_conf=None,
                 sampling_rate=0.0, skip_empty=True):
        self.application = application
        self.sampling_rate = sampling_rate
        self.skip_empty = True

    def getMetadata(self, environ):
        """Get additional data to be included in the log"""
        return {}

    def recordSample(self, data):
        log.info(json.dumps(data))

    def removeMyself(self, stats):
        """Remove objects that get allocated during profiling"""
        for k, v in (["list", 4],
                     ["weakref", 2],
                     ["dict", 2],
                     ["frame", 1],
                     ["add_close", 1],
                     ["listiterator", 1]):
            if k in stats:
                stats[k] -= v
                if stats[k] <= 0:
                    del stats[k]

    def __call__(self, environ, start_response):
        if random.random() > self.sampling_rate:
            return self.application(environ, start_response)

        def close():
            # computing growth failed, skip this
            if not peak_stats:
                return

            try:
                stats = dict(compute_growth(peak_stats=peak_stats))
                self.removeMyself(stats)
                if not stats and self.skip_empty:
                    return
                result = {'growth_stats': stats}
                result.update(self.getMetadata(environ))
                self.recordSample(result)
            except ValueError:
                # Ignore any exceptions that might fire when computing stats
                pass

        peak_stats = {}
        try:
            compute_growth(peak_stats=peak_stats)
        except Exception:
            # Ignore any exceptions that might fire when computing stats
            pass

        return add_close(self.application(environ, start_response), close)


class FlaskObjgraphMiddleware(ObjgraphMiddleware):

    def getServerName(self, environ):
        if 'HTTP_HOST' in environ:
            server_name = environ['HTTP_HOST']
        else:
            server_name = environ['SERVER_NAME']
            if (environ['wsgi.url_scheme'], environ['SERVER_PORT']) not \
               in (('https', '443'), ('http', '80')):
                server_name += ':' + environ['SERVER_PORT']
        return server_name


    def parseUrl(self, environ):
        """Use Flask application to retrieve endpoint and arguments from url"""
        adapter = self.application.url_map.bind(
            self.getServerName(environ),
            script_name=self.application.config['APPLICATION_ROOT'] or '/',
            url_scheme=self.application.config['PREFERRED_URL_SCHEME'])
        return adapter.match(environ['PATH_INFO'], environ['REQUEST_METHOD'])

    def getMetadata(self, environ):
        endpoint, args = self.parseUrl(environ)
        return {'endpoint': endpoint,
                'args': args}


class PyramidObjgraphMiddleware(ObjgraphMiddleware):

    def getMetadata(self, environ):
        route = environ.get('bfg.routes.route', None)
        return {'endpoint': route.name if route is not None else ''}
