def main():
    from optparse import OptionParser
    from .server import create_server

    parser = OptionParser()
    parser.add_option("-p", "--port", type="int", help="Server port")
    parser.add_option("-m", "--module", default='.',
                      help="Module path")
    parser.add_option("-q", "--quiet",
                      action="store_false", dest="verbose", default=True,
                      help="don't print log messages to stdout")
    (options, args) = parser.parse_args()
    if options.verbose:
        print("Listening on port %d..." % (options.port))
    server = create_server(options.module, options.port, options.verbose)
    server.serve_forever()
