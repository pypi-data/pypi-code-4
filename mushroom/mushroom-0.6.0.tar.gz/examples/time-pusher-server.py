#!/usr/bin/env python

from time import time

import gevent

import example_pythonpath
from example_utils import ExampleServer, ExampleStaticFile


class TimePusherServer(ExampleServer):
    urls = [
        ('/', ExampleStaticFile('time-pusher.html')),
    ] + ExampleServer.urls

    def server_init(self):
        gevent.spawn(self.time_loop)

    def time_loop(self):
        while True:
            gevent.sleep(1)
            self.sessions.notify('time', time())


if __name__ == '__main__':
    TimePusherServer.main()
