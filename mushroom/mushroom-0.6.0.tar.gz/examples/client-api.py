#!/usr/bin/env python

import example_pythonpath
from example_utils import ExampleServer, ExampleStaticFile


class ClientApiServer(ExampleServer):
    urls = [
        ('/', ExampleStaticFile('client-api.html')),
    ] + ExampleServer.urls


if __name__ == '__main__':
    ClientApiServer.main()
