import BaseHTTPServer
import gflags
from obhm.load import are_we_overloaded

FLAGS = gflags.FLAGS

gflags.DEFINE_integer('port', 8999, 'Default monitoring port')

class Server(BaseHTTPServer.HTTPServer):
    pass


class Handler(BaseHTTPServer.BaseHTTPRequestHandler):
    def barf(self, reason):
        self.send_response(503)
        self.end_headers()
        self.wfile.write(reason)

    def do_GET(self):
        if are_we_overloaded():
            return self.barf('loadavg too high')
        self.send_response(204)
        self.end_headers()

def run():
    Server(('', FLAGS.port), Handler).serve_forever()

def main(argv):
    try:
        if len(FLAGS(argv)) > 1:
            stderr.write("No positional parameters\\nUsage: %s obhm\\n%s\n" % (sys.argv[0], FLAGS))
            return 1 
    except gflags.FlagsError, e:
        stderr.write("%s\\nUsage: %s obhm\\n%s\n" % (e, sys.argv[0], FLAGS))
        return 1
    return run()
