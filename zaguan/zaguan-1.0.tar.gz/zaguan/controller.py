# -*- coding: utf-8 -*-
import urllib
import inspect

from json import dumps, loads

from zaguan.actions import BaseActionController
from zaguan.container import launch_browser


class WebContainerController(object):
    """Base class for the web containers of the controllers."""
    def __init__(self):
        self.processors = []

    def on_navigation_requested(self, elem, view, frame, req, data=None):
        """This is the Callback executed each time  URI inside the webkit
        object is loaded"""
        uri = req.get_uri()
        self.process_uri(uri)

    def process_uri(self, uri):
        """Procces the url on each processor."""
        for processor in self.processors:
            processor(uri)

    def set_screen(self, screen, **kwargs):
        """Sends the change sreen command to the web interface."""
        self.send_command("change_screen", [screen, kwargs])

    def send_command(self, command, data=None):
        """Inyects the JS in the browser for the givven command."""
        json_data = dumps(data).replace("\\\"", "\\\'")
        self.send_function("run_op('%s', '%s')" % (command, json_data))

    def get_browser(self, uri, settings=[], debug=False, qt=False):
        """Gets the browser objects and prpare it to bo able to be used in it's
        context.
        """
        browser, web_send = launch_browser(uri, echo=debug,
                                           user_settings=settings, qt=qt)
        self.send_function = web_send
        if not qt:
            browser.connect("resource-request-starting",
                            self.on_navigation_requested)
        return browser

    def add_processor(self, url_word, instance):
        def _inner(uri):
            scheme, path = uri.split(':', 1)
            if scheme == "http":
                parts = path.split("/")[2:]
                if parts[0] == url_word:
                    remain = parts[1]
                elif parts[1]  == url_word:
                    remain = parts[2]
                else:
                    remain = None
                if remain is not None:
                    try:
                        action, data = remain.split("?")
                    except ValueError:
                        action = remain
                        data = "null"

                    data = loads(urllib.unquote(data))

                    # search the action at the 'action controller' instance
                    # argument. if we dont find the action, we try to get it
                    # from the controller itself.
                    method = getattr(instance, action, None)
                    if method is None:
                        method = getattr(self, action, None)
                    if not method:
                        raise NotImplementedError()
                    return method(data)

        self.processors.append(_inner)
