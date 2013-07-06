import os

from django.core.wsgi import get_wsgi_application

from twisted.internet import reactor
from twisted.application import service, strports
from twisted.python import filepath
from twisted.web import wsgi, server, static, resource


class WSGIChildrenResource(resource.Resource):
    def __init__(self, reactor, threadPool, application):
        resource.Resource.__init__(self)
        self._root = wsgi.WSGIResource(reactor, threadPool, application)

    def getChild(self, child, request):
        request.prepath.pop()
        request.postpath.insert(0, child)
        return self._root

    def render(self, request):
        return self._root.render(request)


env_base = filepath.FilePath(os.environ['CSAT_ENVDIR'])

# Let django know where to find the settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'csat.webapp.settings')

# Instantiate the WSGI resource and add the children to serve the static files
resource = WSGIChildrenResource(reactor, reactor.getThreadPool(),
                                get_wsgi_application())
resource.putChild(
    'static',
    static.File(filepath.FilePath(__file__).sibling('static').path)
)
resource.putChild(
    'media',
    static.File(env_base.child('media').path)
)

# Create the application object and connect it to the webapp server
site = server.Site(resource)
application = service.Application('csat-webapp')

from csat.webapp.scripts.server import _endpoints as endpoints

tcpService = strports.service(endpoints['webserver'], site)
tcpService.setServiceParent(application)
