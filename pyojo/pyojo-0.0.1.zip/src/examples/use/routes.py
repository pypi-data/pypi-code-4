import pyojo
from pyojo.server import wsgi

"""
@pyojo.route("/")
def Home(request): return ["X"]



@pyojo.route("/class")
class ClassTest(object):
    @pyojo.route("/class2")    
    def get(self):
        pass
"""




@pyojo.command("help")
def HelpCommand(request):
    print "COMMAND HELP"
    return repr(kwargs)

@pyojo.route("/hi")
def _no_args_example():
    return "Hello!"

@pyojo.route("/status/{code}")
def _status_codes(code):
    return int(code)


@pyojo.route("/routes")
def _config_example():
    routes = pyojo.Config.get_route_map()
    return pyojo.pretty(routes)

@pyojo.route("/environ")
def _environ_example(environ):
    return pyojo.pretty(environ)

@pyojo.route("/environ2")
def _environ_example_2(environ):
    e = {}
    for key,value in environ.iteritems():
        if not os.environ.has_key(key):
            e[key]=value
    return pyojo.pretty(e)

@pyojo.route("/request")
def _request_example(request):
    out = {"url": request.url,
           "method": request.method,
           "accept": request.accept,
           "id": id(request),
           "id os.environ": id(os.environ),
           "id environ": id(request.environ)}
    return pyojo.pretty(out)





@pyojo.route("/reply")
class _ResponseExample(pyojo.Response):
    
    def GET(self):
        self.content = "text/plain"
        print self.content
        self.write("GETXXXXXXXXXXXXXXX %s " % self.content)
        self.write("XX")
        
        return self


wsgi.main()
