import httplib
import socket

class UnixHTTPConnection(httplib.HTTPConnection):

    def __init__(self, path, host='localhost', port=None, strict=None,
                 timeout=None):
        httplib.HTTPConnection.__init__(self, host, port=port, strict=strict,
                                        timeout=timeout)
        self.path = path

    def connect(self):
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.connect(self.path)
        self.sock = sock
