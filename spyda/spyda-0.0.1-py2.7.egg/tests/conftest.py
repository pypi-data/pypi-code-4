# Module:   conftest
# Date:     20th December 2012
# Author:   James Mills, j dot mills at griffith dot edu dot au

"""pytest config"""

import pytest

from os import path
from time import sleep
from collections import deque

from circuits.net.sockets import Close
from circuits.web import Controller, Server, Static
from circuits import handler, BaseComponent, Component, Debugger, Manager

TIMEOUT = 0.1
DOCROOT = path.join(path.dirname(__file__), "docroot")


class Watcher(BaseComponent):

    def init(self):
        self.events = deque([], 50)

    @handler(channel="*", priority=999.9)
    def _on_event(self, event, *args, **kwargs):
        self.events.append(event)

    def wait(self, name, channel=None, timeout=3.0):
        for i in range(int(timeout / TIMEOUT)):
            if channel is None:
                for event in self.events:
                    if event.name == name:
                        return True
            else:
                for event in self.events:
                    if event.name == name and channel in event.channels:
                        return True
            sleep(TIMEOUT)


class Root(Controller):

    def hello(self):
        return "Hello World!"

    def unicode(self):
        self.response.headers["Content-Type"] = "text/plain; charset=utf-8"
        return u"Hello World!"

    def external(self):
        return "<a href=\"http://www.google.com\">Google</a>"


class WebApp(Component):

    channel = "web"

    def init(self, docroot=DOCROOT):
        self.docroot = docroot

        self.server = Server(0).register(self)
        Root().register(self)
        Static(docroot=self.docroot).register(self)


@pytest.fixture(scope="session")
def manager(request):
    manager = Manager()

    def finalizer():
        manager.stop()

    request.addfinalizer(finalizer)

    manager.start()

    if request.config.option.verbose:
        Debugger().register(manager)

    return manager


@pytest.fixture(scope="session")
def watcher(request, manager):
    watcher = Watcher().register(manager)

    def finalizer():
        watcher.unregister()

    return watcher


@pytest.fixture(scope="session")
def webapp(request, manager, watcher):
    webapp = WebApp().register(manager)

    def finalizer():
        webapp.fire(Close(), webapp.server)
        webapp.stop()

    request.addfinalizer(finalizer)

    assert watcher.wait("ready", webapp.channel)

    return webapp
