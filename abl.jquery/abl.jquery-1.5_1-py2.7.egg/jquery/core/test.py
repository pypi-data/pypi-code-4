from __future__ import absolute_import

import re
import logging

from webtest import TestApp
from tw.api import make_middleware
from tw.core.testutil import WidgetTestCase


logger = logging.getLogger(__name__)


class TestResource(WidgetTestCase):
    """
    Baseclass for rendering a specific resource
    and all it's dependencies.
    """

    resource = None

    logger = logger

    def test_resource(self):
        if self.resource is None:
            return

        def app(environ, start_response):
            self.resource.inject()
            start_response("200 OK", [("Content-type", "text/html")])
            return ["<html><head></head><body></body></html>"]


        app = make_middleware(app, stack_registry=True, config={})
        self.app = TestApp(app)

        res = self.app.get("/")
        body = res.body

        # try & fetch the included resources, they
        # all must be served
        resources = []
        for _, _, resource in re.findall(r"""(src|href)=(?P<start>'|")(.*?)(?P=start)""", body): #"
            assert resource
            res = self.app.get(resource)
            resources.append(resource)
            self.logger.debug(resource)

        return resources


class TestWidget(WidgetTestCase):
    """
    Baseclass for rendering a specific widget
    and all it's dependencies.
    """

    widget = None

    logger = logger

    args = ()
    kwargs = {}

    def test_widget(self):
        if self.widget is None:
            return

        widget = self.widget(*("testwidget",) + self.args, **self.kwargs)

        def app(environ, start_response):
            w = widget.display().encode("utf-8")
            start_response("200 OK", [("Content-type", "text/html")])
            return ["<html><head></head><body>%s</body></html>" % w ]


        app = make_middleware(app, stack_registry=True, config={})
        self.app = TestApp(app)

        res = self.app.get("/")
        body = res.body

        self.logger.debug(body)
        # try & fetch the included resources, they
        # all must be served
        resources = []
        for _, _, resource in re.findall(r"""(src|href)=(?P<start>'|")(.*?)(?P=start)""", body): #"
            assert resource
            res = self.app.get(resource)
            resources.append(resource)


        return resources


