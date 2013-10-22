def main():
    from optparse import OptionParser
    from .server import create_server, shutdown_competitors

    parser = OptionParser(usage='python -m roc <options>')
    parser.add_option("-p", "--port", type="int", help="Server port")
    parser.add_option("-m", "--module", default='.',
                      help="Module path (default: %default)")
    parser.add_option("-e", "--egoist", default=False,
                      action="store_true",
                      help="Shutdown competitors before start "
                           "(default: %default)")
    parser.add_option("-q", "--quiet",
                      action="store_false", dest="verbose", default=True,
                      help="don't print log messages to stdout "
                           "(default: print)")
    (options, args) = parser.parse_args()
    if options.port is not None:
        port = int(options.port)
        if options.egoist:
            shutdown_competitors(port)
        server = create_server(options.module, port, options.verbose)
        if options.verbose:
            print("Listening on port %d..." % (port))
        server.serve_forever()
    else:
        parser.print_help()
