from twisted.application import internet
from twisted.application.service import IServiceMaker
from twisted.plugin import IPlugin
from twisted.python import usage
from twisted.web import server
from zope.interface import implements

from derrick.resource import DerrickRootResource


class DerrickOptions(usage.Options):
    '''Options for Derrick server.'''
    optParameters = (
        ('port', 'p', 8080, 'The port number to listen for requests.'),
    )


class DerrickServiceMaker(object):
    '''Service Maker for Derrick.'''
    implements(IServiceMaker, IPlugin)

    description = 'A Twisted server for ImpactJS HTML5 game development.'
    options = DerrickOptions
    tapname = 'derrick'

    def makeService(self, options):
        '''Start the service.'''
        factory = server.Site(DerrickRootResource())
        return internet.TCPServer(int(options['port']), factory)

serviceMaker = DerrickServiceMaker()
