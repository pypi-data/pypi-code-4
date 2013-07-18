import time
import datetime

from webob import Request

def chronometer_filter_factory(app, global_conf, **kwargs):
    """
    Factory for pasteDeploy.

    app is a wsgi app,
    global_conf is a dictionnary containing __file__ and here,
    kwargs are args in the parameters passed in the pastedeploy file conf.

    return a ChronoFilter.
    """

    return ChronoFilter(app, **kwargs)


class ChronoFilter(object):
    """
    Wsgi Middleware for mesuring time execution (and display other things).
    """
    def __init__(self, app, **kwargs):
        """
        Constructor.

        app wsgi to chronometer,
        kwargs : conf for ChronoFilter :
          - separator : string for separate fields in display (default: '-'),
          - fields list of fields to display
          .. TODO list fields.
        """
        self._app = app

        if 'separator' in kwargs:
            self._sep = kwargs['separator']
        else:
            self._sep = '-'

        if 'fields' in kwargs:
            self._fields = kwargs['fields'].split()
        else:
            self._fields = []

    def __call__(self, environ, start_response):
        """
        Call of the wsgi app.
        """
        begin = time.time()

        req = Request(environ)
        resp = req.get_response(self._app)

        result = resp(environ, start_response)

        end = time.time()

        choice = {
            'SERVER_SOFTWARE': None, # 'waitress'
            'SCRIPT_NAME': req.script_name,
            'REQUEST_METHOD': req.method,
            'PATH_INFO': req.path_info,
            'SERVER_PROTOCOL': req.http_version,
            'QUERY_STRING': req.query_string,
            'HTTP_USER_AGENT': req.user_agent,
            'SERVER_NAME': req.server_name,
            'REMOTE_ADDR': req.remote_addr,
            'wsgi.url_scheme': req.scheme,
            'SERVER_PORT': str(req.server_port),

            'HTTP_HOST': req.host,
#            'wsgi.multithread': True, # TODO
            'HTTP_ACCEPT': str(req.accept),
#            'wsgi.version': (1, 0),
#            'wsgi.run_once': False,

#            'wsgi.multiprocess': False,
#            'webob._parsed_cookies': ({}, '')
            'STATUS': resp.status,
            'STATUS_CODE': resp.status_code,
            'DATETIME': str(datetime.datetime.now()),
            'TIME': "%.02fms" % ((end- begin) * 1000),
            }


        data = []
        for field in self._fields:
            try:
                data.append(choice[field])
            except KeyError:
                data.append(' ')
        sep = " %s " % (self._sep)
        print sep.join(data)
        return result

# class ProxyToFields(object):
#     req = None
#     resp = None
#     end = None
#     begin = None

#     _fields = {
#             'SERVER_SOFTWARE': None, # 'waitress'
#             'SCRIPT_NAME': req.script_name,
#             'REQUEST_METHOD': req.method,
#             'PATH_INFO': req.path_info,
#             'SERVER_PROTOCOL': req.http_version,
#             'QUERY_STRING': req.query_string,
#             'HTTP_USER_AGENT': req.user_agent,
#             'SERVER_NAME': req.server_name,
#             'REMOTE_ADDR': req.remote_addr,
#             'wsgi.url_scheme': req.scheme,
#             'SERVER_PORT': str(req.server_port),

#             'HTTP_HOST': req.host,
# #            'wsgi.multithread': True, # TODO
#             'HTTP_ACCEPT': str(req.accept),
# #            'wsgi.version': (1, 0),
# #            'wsgi.run_once': False,

# #            'wsgi.multiprocess': False,
# #            'webob._parsed_cookies': ({}, '')
#             'STATUS': resp.status,
#             'STATUS_CODE': resp.status_code,
#             'DATETIME': str(datetime.datetime.now()),
#             'TIME': "%.02fms" % ((end- begin) * 1000),
#             }

