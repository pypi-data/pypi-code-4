#!/usr/bin/env python

import example_pythonpath
from example_utils import ExampleServer, ExampleStaticFile


class PingServer(ExampleServer):
    urls = [
        ('/', ExampleStaticFile('ping.html')),
    ] + ExampleServer.urls

    def rpc_ping(self, request):
        return 'pong'


if __name__ == '__main__':
    PingServer.main()
