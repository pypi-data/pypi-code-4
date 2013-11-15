"""
This is a test HTTP server (which may grow into a HBase Stargate replacement if Stargate does not comply with our
needs). For now it's used just as test server (prints out useful info). Supports GET, POST, PUT, DELETE methods. Does
not do anything, but prints back the debug info about the request.

To start the server, run the following command from terminal:

    $ python http/server.py

And you may now play with various requests using `https://addons.mozilla.org/en-US/firefox/addon/http-resource-test/`
or any other testing tool of your choice.
"""
import sys
import getopt

from twisted.internet import reactor
from twisted.web.server import Site
from twisted.web.resource import Resource

from six import print_

class HBasePage(Resource):
    """
    HBase page.
    """
    isLeaf = True

    def __print_debug_info(self, called_from, request):
        print_('===============================')
        print_(called_from)
        print_(request)
        print_(request.args)
        print_(request.method)
        print_(request.content.readlines())
        print_(request.cookies)
        print_(request.code)
        print_(request.requestHeaders)
        print_(request.responseHeaders)
        #import ipdb; ipdb.set_trace()

    def render_GET(self, request):
        """
        Handles GET requests.
        """
        self.__print_debug_info('GET', request)
        return "<html><body>GET</body></html>"

    def render_POST(self, request):
        """
        Handles POST requests.
        """
        self.__print_debug_info('POST', request)
        import ipdb; ipdb.set_trace()
        return '<html><body>POST</body></html>'

    def render_PUT(self, request):
        """
        Handles PUT requests.
        """
        self.__print_debug_info('PUT', request)
        return '<html><body>PUT</body></html>'

    def render_DELETE(self, request):
        """
        Handles DELETE requests.
        """
        self.__print_debug_info('DELETE', request)
        return '<html><body>DELETE</body></html>'

def main():
    """
    This runs the protocol on port 8000. You can override it by feeding it as an argument to `server.py`.

    :Example:
        $ python src/starbase/server/runserver.py 8001
    """
    # Parse command line options
    try:
        opts, args = getopt.getopt(sys.argv[1:], "h", ["help"])
    except getopt.error as msg:
        print_(msg)
        print_("for help use --help")
        sys.exit(2)

    port = 8000

    # Process options
    for o, a in opts:
        if o in ("-h", "--help"):
            print_(__doc__)
            sys.exit(0)
    # Process arguments
    try:
        port = int(args[0])
    except Exception as e:
        pass

    resource = HBasePage()
    factory = Site(resource)
    reactor.listenTCP(port, factory)
    reactor.run()

# this only runs if the module was *not* imported
if __name__ == '__main__':
    main()
