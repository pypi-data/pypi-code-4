__all__ = ['start_wsgi_server']

from _wsgi import handler as wsgi_app

try:
    from _profile import wsgi_profile
    wsgi_app = wsgi_profile(wsgi_app)
    print "wsgi profiler path: /__profiler__"
except ImportError:
    pass

try:
    from cherrypy import wsgiserver as cpws

    def start_wsgi_server(host = '127.0.0.1', port = 9000, app = wsgi_app):
        print "serving on http://%s:%s" % (host, port)
        s = cpws.CherryPyWSGIServer((host, port), app, request_queue_size = 500)
        try:
            s.start()
        except KeyboardInterrupt:
            s.stop()

except ImportError:
    try:
        from paste import httpserver

        def start_wsgi_server(host = '127.0.0.1', port = 9000, app = wsgi_app):
            httpserver.serve(app, host, port, request_queue_size = 500)

    except ImportError:
        from wsgiref.simple_server import make_server

        def start_wsgi_server(host = '127.0.0.1', port = 9000, app = wsgi_app):
            make_server(host, port, app).serve_forever()

#NOTE: for production use (gunicorn|uwsgi)+nginx+supervisor
