#!/usr/bin/env python

import example_pythonpath
from example_utils import ExampleServer, ExampleStaticFile


class ChatServer(ExampleServer):
    urls = [
        ('/', ExampleStaticFile('chat.html')),
    ] + ExampleServer.urls

    def rpc_message(self, request):
        self.sessions.notify('message', request.data)


if __name__ == '__main__':
    ChatServer.main()
