import pyojo
from pyojo.server import wsgi
from pyojo.js.lib import alert
"""
@pyojo.route("/")
def Home(request): return ["X"]



@pyojo.route("/class")
class ClassTest(object):
    @pyojo.route("/class2")    
    def get(self):
        pass
"""

import pyojo.all

@pyojo.route("/")
def RoutesPage(request):
    command = request.environ
    routes = pyojo.Config.get_route_map()
    return pyojo.pretty(routes)

@pyojo.route("/{.*}")
def AllRoutes(request):
    command = request.environ
    routes = pyojo.Config.get_route_map()
    return "ALL"

wsgi.main()
