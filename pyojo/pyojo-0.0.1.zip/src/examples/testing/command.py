import pyojo
from pyojo import server
from pyojo import pretty


@pyojo.route("/hola")
def Response(request):
    pyojo.Config.command["hola"](111)
    return "HOLITA"





@pyojo.route("/")
def _r_hola(request):
        
    @pyojo.command("error")
    def _c_error(environ):
    	print "Hola consola %s" % pretty(environ)


    pyojo.Config.command["error"](0)

    request.content_type("text/plain")
    return pretty({"* environ": (request.environ),
            "* ROUTES": (pyojo.Config.get_route_map()),
            "* CONFIG": (pyojo.Config),
            "* COMMANDS": (pyojo.Config.command),
            "* TASKS": (pyojo.Config.get_tasks("pending", "GET")),})


@pyojo.command("log")
def _c_log(environ):
    print "Hola consola %s" % pretty(environ)












server.main()
