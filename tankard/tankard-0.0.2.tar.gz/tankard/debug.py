import sys
import argparse


def make_server(app, port=8080):

    def debug_main(argv=sys.argv[1:]):
        parser = argparse.ArgumentParser()
        parser.add_argument("-i", "--interface", default="0.0.0.0")
        parser.add_argument("-p", "--port", type=int, default=port)
        parser.add_argument("-n", "--no-debug", action="store_true")
        args = parser.parse_args(argv)

        app.config["TRAP_BAD_REQUEST_ERRORS"] = True
        app.run(host=args.interface, port=args.port, debug=not args.no_debug)
    return debug_main
