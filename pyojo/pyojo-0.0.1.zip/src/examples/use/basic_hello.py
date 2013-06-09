import pyojo
from pyojo.server import wsgi

@pyojo.route("/")
def Response(request):
    return "Hello World!"

wsgi.main()

#if __name__ == '__main__':
#    from paste import httpserver
#    httpserver.serve(wsgi.application, host='127.0.0.1', port='8080')